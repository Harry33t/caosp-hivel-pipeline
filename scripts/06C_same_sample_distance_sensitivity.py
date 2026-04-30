"""Step 6C: same-sample distance sensitivity.

The headline 221 -> 3 narrative in earlier drafts mixed populations: 221
came from inverse-parallax kinematics on the 1101-star master, while 3
came from Bailer-Jones kinematics on the 356-star final-strict sample.
That conflates the distance effect with the LAMOST quality and RV
consistency cuts. This step recomputes both passes on **the same 356-star
final-strict sample**, so any change in P_unbound reflects only the
choice of distance estimator.

Inputs
------
- data/processed/hivel_gaia_kinematics.parquet     (Step 4B, 1101 rows,
                                                    inverse-parallax)
- data/processed/final_kinematics_strict.parquet   (Step 6B, 356 rows,
                                                    Bailer-Jones)
- data/processed/hivel_final_sample_flags.parquet  (final-strict flag)

Outputs
-------
- data/processed/same_sample_distance_sensitivity.csv
- reports/same_sample_distance_sensitivity.md
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


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step6c")

    # ---- load inputs ----
    flags = pd.read_parquet(PROCESSED_DIR / "hivel_final_sample_flags.parquet")
    strict_ids = set(flags.loc[flags["sample_final_strict"], "source_id"].astype("int64").tolist())
    log.info("final strict source_ids: %d", len(strict_ids))

    inv = pd.read_parquet(PROCESSED_DIR / "hivel_gaia_kinematics.parquet")
    inv["source_id"] = inv["source_id"].astype("int64")
    inv_strict = inv[inv["source_id"].isin(strict_ids)].copy()
    log.info("inverse-parallax pass on strict: %d rows (expected %d)",
             len(inv_strict), len(strict_ids))

    bj = pd.read_parquet(PROCESSED_DIR / "final_kinematics_strict.parquet")
    bj["source_id"] = bj["source_id"].astype("int64")
    log.info("Bailer-Jones pass on strict: %d rows", len(bj))

    # ---- assemble side-by-side comparison ----
    # Inverse-parallax columns from Step 4B: V_GSR (point), V_GSR_mc_mean,
    # V_GSR_mc_std, P_v500, P_unbound. Distance there is 1/parallax.
    # Bailer-Jones columns from Step 6B: same names but distance is BJ;
    # Step 6B renamed P_unbound -> P_unbound_final.
    inv_keep = inv_strict[[
        "source_id", "distance_kpc",
        "V_GSR", "V_GSR_mc_mean", "V_GSR_mc_std",
        "P_v500", "P_unbound",
    ]].rename(columns={
        "distance_kpc":     "distance_kpc_invplx",
        "V_GSR":            "v_grf_invplx",
        "V_GSR_mc_mean":    "v_grf_mc_mean_invplx",
        "V_GSR_mc_std":     "v_grf_mc_std_invplx",
        "P_v500":           "P_v500_invplx",
        "P_unbound":        "P_unbound_invplx",
    })
    bj_keep = bj[[
        "source_id", "distance_pc",
        "V_GSR", "V_GSR_mc_mean", "V_GSR_mc_std",
        "P_v500", "P_unbound_final", "v_esc",
        "catalogs",
    ]].rename(columns={
        "distance_pc":      "distance_pc_bj",
        "V_GSR":            "v_grf_bj",
        "V_GSR_mc_mean":    "v_grf_mc_mean_bj",
        "V_GSR_mc_std":     "v_grf_mc_std_bj",
        "P_v500":           "P_v500_bj",
        "P_unbound_final":  "P_unbound_bj",
    })
    bj_keep["distance_kpc_bj"] = bj_keep["distance_pc_bj"] / 1000.0
    bj_keep = bj_keep.drop(columns=["distance_pc_bj"])

    df = bj_keep.merge(inv_keep, on="source_id", how="inner")
    df["delta_P_unbound"] = df["P_unbound_bj"] - df["P_unbound_invplx"]
    df["distance_ratio_bj_over_invplx"] = (
        df["distance_kpc_bj"] / df["distance_kpc_invplx"]
    )
    log.info("merged same-sample table: %d rows", len(df))

    out_csv = PROCESSED_DIR / "same_sample_distance_sensitivity.csv"
    df["source_id"] = df["source_id"].astype("int64").astype(str)
    df.to_csv(out_csv, index=False)
    log.info("CSV -> %s", out_csv)

    # ---- summary statistics ----
    n = len(df)

    def thr(col, t):
        return int((df[col] > t).sum())

    counts = {
        "P_unbound > 0.5  (inverse parallax)": thr("P_unbound_invplx", 0.5),
        "P_unbound > 0.5  (Bailer-Jones)":     thr("P_unbound_bj",     0.5),
        "P_unbound > 0.7  (inverse parallax)": thr("P_unbound_invplx", 0.7),
        "P_unbound > 0.7  (Bailer-Jones)":     thr("P_unbound_bj",     0.7),
        "P_unbound > 0.9  (inverse parallax)": thr("P_unbound_invplx", 0.9),
        "P_unbound > 0.9  (Bailer-Jones)":     thr("P_unbound_bj",     0.9),
    }
    n_dropped = int(((df["P_unbound_invplx"] > 0.5) & (df["P_unbound_bj"] <= 0.5)).sum())
    n_promoted = int(((df["P_unbound_invplx"] <= 0.5) & (df["P_unbound_bj"] > 0.5)).sum())

    ratio = df["distance_ratio_bj_over_invplx"].dropna()
    rmed = float(ratio.median())
    rmed_unb = float(df.loc[df["P_unbound_invplx"] > 0.5,
                            "distance_ratio_bj_over_invplx"].dropna().median()) \
               if (df["P_unbound_invplx"] > 0.5).any() else np.nan

    # ---- report ----
    md = []
    md.append("# Same-sample distance sensitivity (Step 6C)\n")
    md.append("All numbers below are computed on **the same `sample_final_strict` "
              "of 356 stars**. The two passes differ only in the distance "
              "estimator: inverse parallax ($1000/\\varpi$) vs Bailer-Jones "
              "geometric distance ($r_{\\mathrm{med,geo}}$ from "
              "`external.gaiaedr3_distance`). Proper motions, Gaia DR3 radial "
              "velocities, and the Monte Carlo error budget are otherwise "
              "identical (1000 draws per star).\n")

    md.append("## 1. Counts of unbound candidates on the same 356-star sample\n")
    md.append("| threshold | inverse parallax | Bailer-Jones | net change |")
    md.append("|---|---:|---:|---:|")
    for thr_v in (0.5, 0.7, 0.9):
        a = thr("P_unbound_invplx", thr_v)
        b = thr("P_unbound_bj",     thr_v)
        md.append(f"| $P_{{\\rm unbound}} > {thr_v}$ | {a} | {b} | {b - a:+d} |")
    md.append("")
    md.append(f"Sample size: **N = {n}**.")
    md.append("")

    md.append("## 2. Per-star reclassification\n")
    md.append("| transition (across $P_{\\rm unbound}=0.5$) | count |")
    md.append("|---|---:|")
    md.append(f"| inverse-parallax $>0.5$ $\\rightarrow$ Bailer-Jones $\\le 0.5$ (downgraded) | {n_dropped} |")
    md.append(f"| inverse-parallax $\\le 0.5$ $\\rightarrow$ Bailer-Jones $>0.5$ (promoted)   | {n_promoted} |")
    md.append("")

    md.append("## 3. Distance ratio on the same sample\n")
    md.append(f"- median $r_{{\\rm med,geo}}/(1000/\\varpi)$ (full strict, N={n}): **{rmed:.3f}**")
    if not np.isnan(rmed_unb):
        md.append(f"- median ratio on stars with inverse-parallax "
                  f"$P_{{\\rm unbound}}>0.5$: **{rmed_unb:.3f}**")
    md.append("")

    md.append("## 4. Headline statement (replaces previous master-vs-strict mix)\n")
    inv05 = thr("P_unbound_invplx", 0.5)
    bj05  = thr("P_unbound_bj",     0.5)
    inv09 = thr("P_unbound_invplx", 0.9)
    bj09  = thr("P_unbound_bj",     0.9)
    md.append(
        f"> On the same final-strict sample of {n} stars, replacing "
        f"inverse-parallax distances with Bailer-Jones geometric distances "
        f"reduces the number of likely unbound candidates "
        f"($P_{{\\rm unbound}}>0.5$) from **{inv05}** to **{bj05}**, and the "
        f"number of high-confidence unbound candidates "
        f"($P_{{\\rm unbound}}>0.9$) from **{inv09}** to **{bj09}**. The "
        f"distance estimator alone---not the LAMOST quality or RV-consistency "
        f"cuts---is responsible for the change.\n")

    md.append("## 5. Outputs\n")
    md.append(f"- `{out_csv.relative_to(ROOT)}` (one row per source, both passes side-by-side)")
    md.append("- This report.\n")

    out_md = REPORTS_DIR / "same_sample_distance_sensitivity.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)

    print(f"\nSame-sample (N={n}):")
    for k, v in counts.items():
        print(f"  {k:42s} {v}")
    print(f"  downgraded across 0.5: {n_dropped}, promoted: {n_promoted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
