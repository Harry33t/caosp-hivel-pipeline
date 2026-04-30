"""Step 4A: Gaia x VizieR master sample + quality-control report.

Outputs
-------
data/processed/hivel_gaia_master.parquet
data/processed/hivel_gaia_master.csv
reports/gaia_vizier_qc.md

The master table is one row per unique Gaia DR3 source_id; the
``catalogs`` column lists which input catalogues that source came from
(comma-separated, e.g. "li2021,liao2024").
"""
from __future__ import annotations
import sys
from pathlib import Path
from textwrap import dedent
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, RAW_VIZIER, RAW_GAIA, PROCESSED_DIR
from caosp_hivel.config import catalogs
from caosp_hivel.log import get_logger

REPORTS_DIR = ROOT / "reports"

SOURCE_ID_CANDIDATES = ("source_id", "Gaia", "Source", "GaiaDR3", "GaiaEDR3", "DR3Name")


def _vizier_source_ids(df: pd.DataFrame) -> pd.Series:
    for col in SOURCE_ID_CANDIDATES:
        if col not in df.columns:
            continue
        s = df[col]
        if not pd.api.types.is_numeric_dtype(s):
            s = s.astype(str).str.extract(r"(\d{6,})", expand=False)
        return pd.to_numeric(s, errors="coerce").dropna().astype("int64")
    raise KeyError(f"no Gaia id col in {list(df.columns)[:8]}")


def _fmt_pct(num: int, denom: int) -> str:
    if denom == 0:
        return "n/a"
    return f"{num} ({100 * num / denom:.1f}%)"


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step4a")

    # ---------- load per-catalog vizier + gaia ----------
    cats = catalogs()["vizier"]
    per_cat: dict[str, dict] = {}
    for entry in cats:
        label = entry["label"]
        viz_path = RAW_VIZIER / f"{label}.parquet"
        gaia_path = RAW_GAIA / f"{label}.parquet"
        if not viz_path.exists() or not gaia_path.exists():
            log.error("missing parquet for %s", label)
            return 1
        viz = pd.read_parquet(viz_path)
        gaia = pd.read_parquet(gaia_path)
        viz_ids = set(_vizier_source_ids(viz).tolist())
        gaia_ids = set(gaia["source_id"].astype("int64").tolist())
        per_cat[label] = {
            "entry": entry,
            "viz": viz,
            "gaia": gaia,
            "viz_ids": viz_ids,
            "gaia_ids": gaia_ids,
            "missing_ids": sorted(viz_ids - gaia_ids),
        }
        log.info("%s: vizier=%d gaia=%d missing=%d",
                 label, len(viz_ids), len(gaia_ids), len(viz_ids - gaia_ids))

    # ---------- merge gaia rows, with provenance ----------
    frames = []
    for label, d in per_cat.items():
        df = d["gaia"].copy()
        df["source_catalog"] = label
        frames.append(df)
    long = pd.concat(frames, ignore_index=True)
    log.info("long table: %d rows (with duplicates across catalogs)", len(long))

    # one row per source_id; keep first numeric record, aggregate provenance
    long["source_id"] = long["source_id"].astype("int64")
    catalogs_per_id = long.groupby("source_id")["source_catalog"].apply(
        lambda s: ",".join(sorted(set(s)))
    )
    master = long.drop_duplicates("source_id", keep="first").copy()
    master["catalogs"] = master["source_id"].map(catalogs_per_id)
    master = master.drop(columns=["source_catalog"])
    master["parallax_over_error"] = master["parallax"] / master["parallax_error"]
    log.info("master: %d unique Gaia source_ids", len(master))

    # ---------- duplicate checks ----------
    coord_round = master.assign(
        _ra=master["ra"].round(6), _dec=master["dec"].round(6)
    )
    dup_coord = coord_round[coord_round.duplicated(["_ra", "_dec"], keep=False)]
    name_col = next((c for c in ("Name", "name", "MAIN_ID") if c in master.columns), None)
    dup_name = master[master.duplicated(name_col, keep=False)] if name_col else None

    # ---------- pairwise overlaps ----------
    labels = list(per_cat.keys())
    overlap = {}
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            inter = per_cat[a]["gaia_ids"] & per_cat[b]["gaia_ids"]
            overlap[f"{a} ∩ {b}"] = len(inter)
    triple = set.intersection(*(per_cat[l]["gaia_ids"] for l in labels))

    # ---------- missing-data stats on master ----------
    n = len(master)

    def miss(col: str) -> int:
        return int(master[col].isna().sum()) if col in master.columns else n

    stats = {
        "parallax": miss("parallax"),
        "parallax_error": miss("parallax_error"),
        "parallax_over_error_NaN": int(master["parallax_over_error"].isna().sum()),
        "radial_velocity": miss("radial_velocity"),
        "radial_velocity_error": miss("radial_velocity_error"),
        "phot_g_mean_mag": miss("phot_g_mean_mag"),
        "phot_bp_mean_mag": miss("phot_bp_mean_mag"),
        "phot_rp_mean_mag": miss("phot_rp_mean_mag"),
        "ruwe": miss("ruwe"),
    }

    ruwe = master["ruwe"].dropna()
    ruwe_q = ruwe.quantile([0.25, 0.5, 0.75, 0.9, 0.99]).round(3).to_dict() if len(ruwe) else {}

    cnt_ruwe_ok = int((master["ruwe"] < 1.4).sum())
    cnt_pl_ok = int((master["parallax_over_error"] > 5).sum())
    cnt_rv_ok = int(master["radial_velocity"].notna().sum())
    cnt_all_ok = int(
        ((master["ruwe"] < 1.4)
         & (master["parallax_over_error"] > 5)
         & master["radial_velocity"].notna()).sum()
    )

    # ---------- write outputs ----------
    out_parquet = PROCESSED_DIR / "hivel_gaia_master.parquet"
    out_csv = PROCESSED_DIR / "hivel_gaia_master.csv"
    master.to_parquet(out_parquet, index=False)
    master.to_csv(out_csv, index=False)
    log.info("master -> %s + .csv", out_parquet)

    # ---------- QC markdown ----------
    li2021 = per_cat["li2021"]
    miss_li2021 = li2021["missing_ids"]
    md_lines = []
    md_lines.append("# Gaia × VizieR master sample QC report\n")
    md_lines.append(f"Generated automatically by `scripts/04A_build_gaia_master_qc.py`.\n")
    md_lines.append("## 1. Per-catalogue counts\n")
    md_lines.append("| catalog | VizieR rows | Gaia DR3 hit | missing |")
    md_lines.append("|---|---:|---:|---:|")
    for label, d in per_cat.items():
        md_lines.append(
            f"| {label} ({d['entry']['id']}) | {len(d['viz_ids'])} | "
            f"{len(d['gaia_ids'])} | {len(d['missing_ids'])} |"
        )
    md_lines.append("")

    md_lines.append("## 2. li2021 missing source_ids (10)\n")
    md_lines.append("These VizieR `Gaia` ids returned no row from `gaiadr3.gaia_source`. "
                    "Most likely they were merged or removed between EDR3 and DR3.\n")
    md_lines.append("```")
    for sid in miss_li2021:
        md_lines.append(str(sid))
    md_lines.append("```\n")

    md_lines.append("## 3. Pairwise & triple overlaps (Gaia hits)\n")
    md_lines.append("| pair | shared sources |")
    md_lines.append("|---|---:|")
    for k, v in overlap.items():
        md_lines.append(f"| {k} | {v} |")
    md_lines.append(f"| all three | {len(triple)} |\n")

    md_lines.append("## 4. Duplicate diagnostics (master table)\n")
    md_lines.append(f"- master rows (unique source_id): **{n}**")
    md_lines.append(f"- duplicated source_id: **{int(master['source_id'].duplicated().sum())}** (should be 0)")
    md_lines.append(f"- duplicate (ra, dec) rounded to 1e-6 deg: **{len(dup_coord)} rows in {dup_coord.duplicated(['_ra','_dec']).sum()} groups**")
    if name_col is not None and dup_name is not None:
        md_lines.append(f"- duplicate names (`{name_col}`): **{len(dup_name)} rows**")
    md_lines.append("")

    md_lines.append("## 5. Missing-value counts in master table\n")
    md_lines.append(f"Total rows = {n}.\n")
    md_lines.append("| field | NaN count | NaN % |")
    md_lines.append("|---|---:|---:|")
    for k, v in stats.items():
        md_lines.append(f"| {k} | {v} | {100*v/n:.1f}% |")
    md_lines.append("")

    md_lines.append("## 6. RUWE distribution\n")
    if ruwe_q:
        md_lines.append("| quantile | RUWE |")
        md_lines.append("|---|---:|")
        for q, v in ruwe_q.items():
            md_lines.append(f"| {int(q*100)}% | {v} |")
        md_lines.append("")

    md_lines.append("## 7. Filter counts\n")
    md_lines.append("| filter | count | %% of master |")
    md_lines.append("|---|---:|---:|")
    md_lines.append(f"| ruwe < 1.4 | {cnt_ruwe_ok} | {100*cnt_ruwe_ok/n:.1f}% |")
    md_lines.append(f"| parallax_over_error > 5 | {cnt_pl_ok} | {100*cnt_pl_ok/n:.1f}% |")
    md_lines.append(f"| radial_velocity not null | {cnt_rv_ok} | {100*cnt_rv_ok/n:.1f}% |")
    md_lines.append(f"| all three above | {cnt_all_ok} | {100*cnt_all_ok/n:.1f}% |")
    md_lines.append("")

    md_lines.append("## 8. Output files\n")
    md_lines.append(f"- `{out_parquet.relative_to(ROOT)}`")
    md_lines.append(f"- `{out_csv.relative_to(ROOT)}`")
    md_lines.append("")

    out_md = REPORTS_DIR / "gaia_vizier_qc.md"
    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    log.info("QC report -> %s", out_md)

    print(f"\nMaster: {n} unique sources")
    print(f"  ruwe<1.4 & plx/err>5 & RV not null: {cnt_all_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
