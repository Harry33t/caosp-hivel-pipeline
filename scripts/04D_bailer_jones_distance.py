"""Step 4D: attach Bailer-Jones (2021) geometric distances.

Source: ``external.gaiaedr3_distance`` table on the Gaia archive
(Bailer-Jones et al. 2021, AJ 161, 147). EDR3 source_ids are compatible
with DR3 source_ids for >99.9 % of stars; we report any unmatched IDs.

This step does NOT recompute kinematics — only attach distances and a
sensitivity comparison to 1000/parallax.

Inputs
------
- data/processed/hivel_final_sample_flags.parquet

Outputs
-------
- data/processed/hivel_with_bailer_jones_distance.parquet
- data/processed/hivel_with_bailer_jones_distance.csv
- reports/distance_upgrade_bailer_jones.md
- reports/figures/distance_inverse_vs_bj.png
- reports/figures/distance_ratio_distribution.png
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.table import Table
from astroquery.gaia import Gaia

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, PROCESSED_DIR, CACHE_DIR
from caosp_hivel.config import settings
from caosp_hivel.log import get_logger

REPORTS_DIR = ROOT / "reports"
FIG_DIR = REPORTS_DIR / "figures"
BJ_CACHE = CACHE_DIR / "bailer_jones_geo.parquet"


def fetch_bailer_jones(source_ids: list[int]) -> pd.DataFrame:
    """Pull r_med_geo / r_lo_geo / r_hi_geo for the given source_ids.
    Caches the result to ``cache/bailer_jones_geo.parquet`` for resumability."""
    log = get_logger("caosp.step4d")
    if BJ_CACHE.exists():
        cached = pd.read_parquet(BJ_CACHE)
        if set(cached["source_id"]) >= set(source_ids):
            log.info("BJ cache hit (%d rows)", len(cached))
            return cached
        log.info("BJ cache stale, refetching")

    chunk_size = int(settings()["gaia"]["upload_chunk_size"])
    parts = []
    for i in range(0, len(source_ids), chunk_size):
        ids = source_ids[i:i + chunk_size]
        upload_path = CACHE_DIR / f"bj_upload_{i:04d}.xml"
        Table({"source_id": ids}).write(upload_path, format="votable", overwrite=True)
        log.info("BJ chunk %d: %d ids", i // chunk_size, len(ids))
        try:
            job = Gaia.launch_job_async(
                query=(
                    "SELECT u.source_id, b.r_med_geo, b.r_lo_geo, b.r_hi_geo, b.flag "
                    "FROM external.gaiaedr3_distance AS b "
                    "JOIN tap_upload.ids AS u USING (source_id)"
                ),
                upload_resource=str(upload_path),
                upload_table_name="ids",
            )
            df = job.get_results().to_pandas()
            parts.append(df)
        finally:
            upload_path.unlink(missing_ok=True)

    out = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["source_id", "r_med_geo", "r_lo_geo", "r_hi_geo", "flag"]
    )
    out["source_id"] = out["source_id"].astype("int64")
    out.to_parquet(BJ_CACHE, index=False)
    log.info("BJ fetched: %d / %d source_ids", len(out), len(source_ids))
    return out


def _figure_inverse_vs_bj(df: pd.DataFrame, path: Path) -> None:
    sub = df.dropna(subset=["bj_distance_pc", "distance_pc_inverse_parallax"])
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(6, 6))
    qmask = sub["q_plx"].fillna(False)
    ax.scatter(sub.loc[~qmask, "distance_pc_inverse_parallax"],
               sub.loc[~qmask, "bj_distance_pc"], s=8, alpha=0.4,
               color="tab:gray", label="parallax_over_error ≤ 5")
    ax.scatter(sub.loc[qmask, "distance_pc_inverse_parallax"],
               sub.loc[qmask, "bj_distance_pc"], s=8, alpha=0.6,
               color="tab:blue", label="parallax_over_error > 5")
    lo = max(min(sub["distance_pc_inverse_parallax"].min(),
                 sub["bj_distance_pc"].min()), 1)
    hi = max(sub["distance_pc_inverse_parallax"].max(),
             sub["bj_distance_pc"].max())
    ax.plot([lo, hi], [lo, hi], "k--", lw=1, label="y = x")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("1000 / parallax  (pc)")
    ax.set_ylabel("Bailer-Jones r_med_geo  (pc)")
    ax.set_title("Distance comparison (1101 master)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def _figure_ratio_hist(df: pd.DataFrame, path: Path) -> None:
    sub = df.dropna(subset=["distance_ratio_bj_over_invplx"])
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bins = np.linspace(0, 3, 80)
    qmask = sub["q_plx"].fillna(False)
    ax.hist(sub.loc[qmask, "distance_ratio_bj_over_invplx"], bins=bins,
            alpha=0.7, label=f"parallax_over_error > 5 ({int(qmask.sum())})",
            color="tab:blue")
    ax.hist(sub.loc[~qmask, "distance_ratio_bj_over_invplx"], bins=bins,
            alpha=0.5, label=f"parallax_over_error ≤ 5 ({int((~qmask).sum())})",
            color="tab:orange")
    ax.axvline(1.0, color="k", lw=1, ls="--", label="ratio = 1")
    ax.set_xlabel("BJ distance / inverse-parallax distance")
    ax.set_ylabel("count")
    ax.set_title("Distance ratio distribution")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step4d")

    src = PROCESSED_DIR / "hivel_final_sample_flags.parquet"
    if not src.exists():
        log.error("missing %s — run step 6 first", src)
        return 1
    df = pd.read_parquet(src)
    log.info("master loaded: %d rows", len(df))

    bj = fetch_bailer_jones(df["source_id"].astype("int64").tolist())
    bj_renamed = bj.rename(columns={
        "r_med_geo": "bj_r_med_geo",
        "r_lo_geo": "bj_r_lo_geo",
        "r_hi_geo": "bj_r_hi_geo",
        "flag": "bj_flag",
    })

    out = df.merge(bj_renamed, on="source_id", how="left")
    out["bj_distance_pc"] = out["bj_r_med_geo"]
    out["bj_distance_kpc"] = out["bj_r_med_geo"] / 1000.0
    out["bj_distance_err_low"]  = out["bj_r_med_geo"] - out["bj_r_lo_geo"]
    out["bj_distance_err_high"] = out["bj_r_hi_geo"] - out["bj_r_med_geo"]
    out["distance_pc_inverse_parallax"] = 1000.0 / out["parallax"]
    out["distance_ratio_bj_over_invplx"] = (
        out["bj_distance_pc"] / out["distance_pc_inverse_parallax"]
    )

    out_pq = PROCESSED_DIR / "hivel_with_bailer_jones_distance.parquet"
    out_csv = PROCESSED_DIR / "hivel_with_bailer_jones_distance.csv"
    out.to_parquet(out_pq, index=False)
    out.to_csv(out_csv, index=False)
    log.info("master + BJ -> %s + .csv", out_pq)

    # figures
    fig_path1 = FIG_DIR / "distance_inverse_vs_bj.png"
    fig_path2 = FIG_DIR / "distance_ratio_distribution.png"
    _figure_inverse_vs_bj(out, fig_path1)
    _figure_ratio_hist(out, fig_path2)
    log.info("figures -> %s, %s", fig_path1, fig_path2)

    # ---------- report ----------
    n_master = len(out)
    n_bj = int(out["bj_distance_pc"].notna().sum())
    n_only = int((out["sample_gaia_only_clean"] & out["bj_distance_pc"].notna()).sum())
    n_strict = int((out["sample_final_strict"] & out["bj_distance_pc"].notna()).sum())
    n_only_total = int(out["sample_gaia_only_clean"].sum())
    n_strict_total = int(out["sample_final_strict"].sum())
    n_unmatched = n_master - n_bj
    unmatched_ids = out.loc[out["bj_distance_pc"].isna(), "source_id"].astype("int64").tolist()

    ratio = out["distance_ratio_bj_over_invplx"].dropna()
    ratio_q5 = out.loc[out["q_plx"].fillna(False), "distance_ratio_bj_over_invplx"].dropna()

    md = []
    md.append("# Distance upgrade: Bailer-Jones (2021) geometric distances\n")
    md.append("Generated by `scripts/04D_bailer_jones_distance.py`. Catalogue: "
              "`external.gaiaedr3_distance` (Bailer-Jones et al. 2021, AJ 161, 147).\n")
    md.append("> **Note on EDR3 vs DR3 source_ids.** Bailer-Jones distances are "
              "indexed by Gaia EDR3 source_id; the EDR3 → DR3 source_id mapping is "
              "stable for the vast majority of stars (a small fraction got merged or "
              "split). Any unmatched IDs are listed below.\n")

    md.append("## 1. Match counts\n")
    md.append("| stage | total | BJ matched | %% |")
    md.append("|---|---:|---:|---:|")
    md.append(f"| master | {n_master} | {n_bj} | {100*n_bj/n_master:.1f}% |")
    md.append(f"| sample_gaia_only_clean | {n_only_total} | {n_only} | "
              f"{100*n_only/max(n_only_total,1):.1f}% |")
    md.append(f"| sample_final_strict | {n_strict_total} | {n_strict} | "
              f"{100*n_strict/max(n_strict_total,1):.1f}% |")
    md.append("")
    if n_unmatched:
        md.append(f"### Unmatched source_ids ({n_unmatched})\n")
        md.append("```")
        for sid in unmatched_ids:
            md.append(str(sid))
        md.append("```\n")

    md.append("## 2. Distance ratio: BJ / (1000/parallax)\n")
    md.append("| sample | N | median | MAD | p90 | p99 |")
    md.append("|---|---:|---:|---:|---:|---:|")
    if len(ratio):
        med = float(ratio.median())
        mad = float((ratio - med).abs().median())
        md.append(f"| all matched | {len(ratio)} | {med:.4f} | {mad:.4f} | "
                  f"{ratio.quantile(0.9):.4f} | {ratio.quantile(0.99):.4f} |")
    if len(ratio_q5):
        med = float(ratio_q5.median())
        mad = float((ratio_q5 - med).abs().median())
        md.append(f"| parallax_over_error > 5 | {len(ratio_q5)} | {med:.4f} | "
                  f"{mad:.4f} | {ratio_q5.quantile(0.9):.4f} | "
                  f"{ratio_q5.quantile(0.99):.4f} |")
    md.append("")

    if len(ratio):
        worst = out.loc[ratio.abs().sub(1).abs().sort_values(ascending=False).index[:5]]
        md.append("## 3. Largest BJ vs 1/parallax disagreements (worst 5)\n")
        cols = ["source_id", "catalogs", "parallax", "parallax_over_error",
                "distance_pc_inverse_parallax", "bj_distance_pc",
                "distance_ratio_bj_over_invplx"]
        cols = [c for c in cols if c in worst.columns]
        md.append("| " + " | ".join(cols) + " |")
        md.append("|" + "|".join("---" for _ in cols) + "|")
        for _, r in worst[cols].iterrows():
            cells = []
            for c in cols:
                v = r[c]
                if isinstance(v, float):
                    cells.append(f"{v:.3f}")
                else:
                    cells.append(str(v))
            md.append("| " + " | ".join(cells) + " |")
        md.append("")

    md.append("## 4. Top-50 preliminary unbound candidates: distance change\n")
    top_path = PROCESSED_DIR / "top_unbound_candidates.csv"
    if top_path.exists():
        top = pd.read_csv(top_path)
        joined = top.merge(
            out[["source_id", "bj_distance_pc",
                 "distance_pc_inverse_parallax",
                 "distance_ratio_bj_over_invplx",
                 "sample_final_strict"]],
            on="source_id", how="left",
        )
        n_with_bj = int(joined["bj_distance_pc"].notna().sum())
        rmean = joined["distance_ratio_bj_over_invplx"].dropna()
        md.append(f"- Top-50 with BJ distance: {n_with_bj}/{len(top)}")
        if len(rmean):
            md.append(f"- median(BJ/inv-plx) on Top-50: **{float(rmean.median()):.3f}**")
            md.append(f"- p90 ratio: {float(rmean.quantile(0.9)):.3f}")
            md.append(f"- min/max ratio: {float(rmean.min()):.3f} / {float(rmean.max()):.3f}")
        md.append("")

    md.append("## 5. Caveats\n")
    md.append("- Step 4B kinematics are based on the **inverse-parallax preliminary** distance; "
              "they are kept on disk only for sensitivity comparison.")
    md.append("- Step 6B will use **Bailer-Jones r_med_geo as the default distance** for the "
              "final kinematic solution. Stars without a BJ match will fall back to "
              "1000/parallax with `distance_source = inverse_parallax_fallback`.")
    md.append("- Inverse-parallax bias grows for `parallax_over_error < 5`; the "
              "`q_plx` flag (>5) marks where the two estimates agree well.")
    md.append("")

    md.append("## 6. Outputs\n")
    md.append(f"- `{out_pq.relative_to(ROOT)}`")
    md.append(f"- `{out_csv.relative_to(ROOT)}`")
    md.append(f"- `{fig_path1.relative_to(ROOT)}`")
    md.append(f"- `{fig_path2.relative_to(ROOT)}`")
    md.append("")

    out_md = REPORTS_DIR / "distance_upgrade_bailer_jones.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)

    print(f"\nBJ matched: {n_bj}/{n_master}, "
          f"strict: {n_strict}/{n_strict_total}, "
          f"unmatched: {n_unmatched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
