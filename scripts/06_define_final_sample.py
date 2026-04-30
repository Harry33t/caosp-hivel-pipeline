"""Step 6: define sample flags and the analysis-ready sub-samples.

This step does NOT recompute kinematics. It only attaches boolean flags so
that downstream steps (4D, 6B, 7, 8, 9) can pick the right population.

Inputs
------
- data/processed/hivel_gaia_lamost_master.parquet
- data/processed/top_unbound_candidates.csv

Outputs
-------
- data/processed/hivel_final_sample_flags.parquet
- data/processed/hivel_final_sample_flags.csv
- data/processed/final_strict_sample.csv
- data/processed/rv_outlier_followup.csv
- data/processed/top_candidates_final_strict_preliminary.csv
- reports/final_sample_definition.md
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, PROCESSED_DIR
from caosp_hivel.log import get_logger

REPORTS_DIR = ROOT / "reports"

# Hard counts the user wants surfaced in the funnel (from earlier steps).
N_VIZIER = 1198
N_GAIA_HIT = 1188


def _max_band_snr(df: pd.DataFrame) -> pd.Series:
    bands = [c for c in ("lamost_snrg", "lamost_snrr",
                          "lamost_snri", "lamost_snrz") if c in df.columns]
    if not bands:
        return pd.Series(np.nan, index=df.index)
    return df[bands].max(axis=1, skipna=True)


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step6")

    src = PROCESSED_DIR / "hivel_gaia_lamost_master.parquet"
    if not src.exists():
        log.error("missing %s — run step 5 first", src)
        return 1
    df = pd.read_parquet(src)
    log.info("master loaded: %d rows", len(df))

    # ---- 1. Gaia astrometry quality ----
    df["q_ruwe"] = df["ruwe"] < 1.4
    df["q_plx"] = (df["parallax"] > 0) & (df["parallax_over_error"] > 5)
    df["q_gaia_astrometry"] = df["q_ruwe"] & df["q_plx"]

    # ---- 2. RV availability + consistency ----
    df["q_gaia_rv"] = df["radial_velocity"].notna()
    df["q_lamost"] = df["has_lamost"].astype(bool)
    df["q_lamost_rv"] = df["lamost_rv"].notna()
    # delta_rv was already added in step 5; recompute defensively
    df["delta_rv"] = df["lamost_rv"] - df["radial_velocity"]
    both_rv = df["q_gaia_rv"] & df["q_lamost_rv"]
    df["q_rv_consistent"] = both_rv & (df["delta_rv"].abs() <= 50)
    df["rv_outlier"] = both_rv & (df["delta_rv"].abs() > 50)

    # ---- 3. LAMOST physical-parameter quality ----
    df["q_lamost_params"] = (
        df["q_lamost"]
        & df["lamost_teff"].notna()
        & df["lamost_logg"].notna()
        & df["lamost_feh"].notna()
    )
    # SNR: prefer lamost_best_snr, fall back to max-of-bands
    if "lamost_best_snr" in df.columns and df["lamost_best_snr"].notna().any():
        snr = df["lamost_best_snr"]
        snr_used = "lamost_best_snr"
    else:
        snr = _max_band_snr(df)
        snr_used = "max(snrg, snrr, snri, snrz)"
    df["lamost_snr_used"] = snr
    df["q_lamost_snr"] = (snr >= 20).fillna(False)
    df["q_lamost_quality"] = df["q_lamost_params"] & df["q_lamost_snr"]

    # ---- 4. Analysis samples ----
    df["sample_gaia_only_clean"]   = df["q_gaia_astrometry"] & df["q_gaia_rv"]
    df["sample_gaia_lamost_clean"] = df["q_gaia_astrometry"] & df["q_gaia_rv"] & df["q_lamost_quality"]
    df["sample_final_strict"]      = df["sample_gaia_lamost_clean"] & df["q_rv_consistent"]
    df["sample_rv_outlier_followup"] = (
        df["q_gaia_astrometry"] & df["q_gaia_rv"] & df["q_lamost_quality"] & df["rv_outlier"]
    )

    # ---- 5. Velocity-based preliminary flags ----
    df["preliminary_unbound"] = df["P_unbound"].fillna(-1) > 0.5
    df["high_conf_unbound"]   = df["P_unbound"].fillna(-1) > 0.9
    df["very_high_velocity"]  = df["V_GSR"].fillna(-1) > 500

    # ---- write outputs ----
    out_pq = PROCESSED_DIR / "hivel_final_sample_flags.parquet"
    out_csv = PROCESSED_DIR / "hivel_final_sample_flags.csv"
    df.to_parquet(out_pq, index=False)
    df.to_csv(out_csv, index=False)
    log.info("flags table -> %s + .csv", out_pq)

    strict_path = PROCESSED_DIR / "final_strict_sample.csv"
    df[df["sample_final_strict"]].to_csv(strict_path, index=False)

    rvout_path = PROCESSED_DIR / "rv_outlier_followup.csv"
    df[df["sample_rv_outlier_followup"]].to_csv(rvout_path, index=False)

    # Top-50 unbound candidates ∩ final strict
    top_path = PROCESSED_DIR / "top_unbound_candidates.csv"
    if top_path.exists():
        top = pd.read_csv(top_path)
        joined = top.merge(
            df[["source_id", "sample_final_strict",
                "lamost_teff", "lamost_logg", "lamost_feh", "lamost_rv",
                "lamost_rv_err", "delta_rv", "rv_outlier", "lamost_n_matches",
                "lamost_designation"]],
            on="source_id", how="left",
        )
        in_strict = joined[joined["sample_final_strict"].fillna(False)]
        top_strict_path = PROCESSED_DIR / "top_candidates_final_strict_preliminary.csv"
        in_strict.to_csv(top_strict_path, index=False)
    else:
        top = pd.DataFrame()
        in_strict = pd.DataFrame()
        top_strict_path = None

    # ---------- report ----------
    n = len(df)
    counts = {
        "VizieR rows": N_VIZIER,
        "Gaia DR3 hit": N_GAIA_HIT,
        "unique Gaia source_id (master)": n,
        "q_gaia_astrometry": int(df["q_gaia_astrometry"].sum()),
        "sample_gaia_only_clean": int(df["sample_gaia_only_clean"].sum()),
        "Gaia × LAMOST matched (q_lamost)": int(df["q_lamost"].sum()),
        "q_lamost_quality (params + SNR>=20)": int(df["q_lamost_quality"].sum()),
        "sample_gaia_lamost_clean": int(df["sample_gaia_lamost_clean"].sum()),
        "sample_final_strict": int(df["sample_final_strict"].sum()),
        "sample_rv_outlier_followup": int(df["sample_rv_outlier_followup"].sum()),
    }

    md = []
    md.append("# Final sample definition (Step 6)\n")
    md.append("Generated by `scripts/06_define_final_sample.py`. "
              "No kinematics were recomputed — this step only attaches boolean flags.\n")

    md.append("## 1. Sample funnel\n")
    md.append("| stage | count |")
    md.append("|---|---:|")
    for k, v in counts.items():
        md.append(f"| {k} | {v} |")
    md.append("")

    md.append("## 2. Flag definitions\n")
    md.append("| flag | definition |")
    md.append("|---|---|")
    flag_defs = [
        ("q_ruwe",            "ruwe < 1.4"),
        ("q_plx",             "parallax > 0 ∧ parallax_over_error > 5"),
        ("q_gaia_astrometry", "q_ruwe ∧ q_plx"),
        ("q_gaia_rv",         "Gaia radial_velocity not null"),
        ("q_lamost",          "Cross-matched to LAMOST (within 1 arcsec)"),
        ("q_lamost_rv",       "lamost_rv not null"),
        ("delta_rv",          "lamost_rv − radial_velocity (km/s)"),
        ("q_rv_consistent",   "|delta_rv| ≤ 50 km/s, only when both RVs exist"),
        ("rv_outlier",        "|delta_rv| > 50 km/s, only when both RVs exist"),
        ("q_lamost_params",   "q_lamost ∧ lamost_teff ∧ lamost_logg ∧ lamost_feh all not null"),
        ("q_lamost_snr",      f"{snr_used} ≥ 20"),
        ("q_lamost_quality",  "q_lamost_params ∧ q_lamost_snr"),
        ("sample_gaia_only_clean",   "q_gaia_astrometry ∧ q_gaia_rv"),
        ("sample_gaia_lamost_clean", "q_gaia_astrometry ∧ q_gaia_rv ∧ q_lamost_quality"),
        ("sample_final_strict",      "sample_gaia_lamost_clean ∧ q_rv_consistent"),
        ("sample_rv_outlier_followup", "q_gaia_astrometry ∧ q_gaia_rv ∧ q_lamost_quality ∧ rv_outlier"),
        ("preliminary_unbound", "P_unbound > 0.5"),
        ("high_conf_unbound",   "P_unbound > 0.9"),
        ("very_high_velocity",  "V_GSR > 500 km/s"),
    ]
    for f, d in flag_defs:
        md.append(f"| `{f}` | {d} |")
    md.append("")

    md.append("## 3. Final-strict per source catalog\n")
    md.append("| source catalog | rows | in final_strict | %% |")
    md.append("|---|---:|---:|---:|")
    for label in ("li2021", "li2023", "liao2024"):
        sel = df["catalogs"].fillna("").str.contains(label)
        a = int(sel.sum())
        b = int((sel & df["sample_final_strict"]).sum())
        md.append(f"| {label} | {a} | {b} | {100*b/max(a,1):.1f}% |")
    md.append("")

    md.append("## 4. Top-50 unbound candidates → final strict\n")
    if not top.empty:
        n_top = len(top)
        n_top_strict = int(in_strict.shape[0])
        n_top_lamost = int(top.merge(df[["source_id","q_lamost"]], on="source_id", how="left")["q_lamost"].fillna(False).sum())
        md.append(f"- Total Top-50: {n_top}")
        md.append(f"- Top-50 with any LAMOST match: {n_top_lamost}")
        md.append(f"- Top-50 in `sample_final_strict`: **{n_top_strict}**")
        md.append(f"- Output: `{top_strict_path.relative_to(ROOT)}`")
    md.append("")

    md.append("## 5. RV outliers (|Δrv| > 50 km/s)\n")
    rv_out = df[df["rv_outlier"]].copy()
    n_followup = int(df["sample_rv_outlier_followup"].sum())
    md.append(f"Total RV outliers in master: **{len(rv_out)}**. "
              f"Of these, **{n_followup}** also pass `q_gaia_astrometry` and "
              "`q_lamost_quality` and are exported to "
              "`data/processed/rv_outlier_followup.csv` (the rest fail the "
              "Gaia astrometry / LAMOST SNR / LAMOST-params gates and live only "
              "in the master table). All RV outliers are excluded from "
              "`sample_final_strict`. None are deleted.\n")
    if len(rv_out):
        cols = ["source_id", "catalogs", "ra", "dec",
                "lamost_obsid", "lamost_designation",
                "radial_velocity", "radial_velocity_error",
                "lamost_rv", "lamost_rv_err", "delta_rv",
                "lamost_n_matches",
                "V_GSR", "P_unbound", "ruwe", "parallax_over_error"]
        cols = [c for c in cols if c in rv_out.columns]
        md.append("| " + " | ".join(cols) + " |")
        md.append("|" + "|".join("---" for _ in cols) + "|")
        for _, r in rv_out[cols].iterrows():
            cells = []
            for c in cols:
                v = r[c]
                if isinstance(v, float):
                    cells.append(f"{v:.3f}" if abs(v) < 1e6 else f"{v:.0f}")
                else:
                    cells.append(str(v))
            md.append("| " + " | ".join(cells) + " |")
        md.append("")

    md.append("## 6. SNR threshold sensitivity\n")
    md.append(f"- SNR field used: **{snr_used}**")
    have_snr = df["lamost_snr_used"].notna().sum()
    md.append(f"- Stars with at least one LAMOST band SNR available: {int(have_snr)}")
    if have_snr:
        for thr in (10, 20, 30, 50):
            k = int((df["lamost_snr_used"] >= thr).sum())
            md.append(f"- snr ≥ {thr}: {k}")
    md.append("")

    md.append("## 7. Sample-usage recommendation for the paper\n")
    md.append("- **Background kinematics figures (Fig 2, 4, 5)**: use `sample_gaia_only_clean` "
              "(the broadest set with reliable Gaia astrometry + Gaia RV; not LAMOST-restricted).")
    md.append("- **LAMOST physical-parameter analysis, ML candidate ranking, Top-candidate Table 3**: "
              "use `sample_final_strict`.")
    md.append("- **RV outliers (3 stars)**: report separately under \"possible binaries / variable-RV "
              "objects requiring follow-up spectroscopy\". Do NOT delete; do NOT include in the "
              "headline candidate table.")
    md.append("")

    md.append("## 8. Outputs\n")
    md.append(f"- `{out_pq.relative_to(ROOT)}`")
    md.append(f"- `{out_csv.relative_to(ROOT)}`")
    md.append(f"- `{strict_path.relative_to(ROOT)}` ({int(df['sample_final_strict'].sum())} rows)")
    md.append(f"- `{rvout_path.relative_to(ROOT)}` ({int(df['sample_rv_outlier_followup'].sum())} rows)")
    if top_strict_path:
        md.append(f"- `{top_strict_path.relative_to(ROOT)}`")
    md.append("")

    out_md = REPORTS_DIR / "final_sample_definition.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)

    print("\nFunnel:")
    for k, v in counts.items():
        print(f"  {k:42s} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
