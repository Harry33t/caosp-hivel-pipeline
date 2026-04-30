"""Step 6B: final kinematics with Bailer-Jones distance + Gaia/LAMOST RV.

- Default distance: bj_r_med_geo (BJ 2021).
- Fallback distance: 1000/parallax  with distance_source = "inverse_parallax_fallback".
- Default RV: Gaia DR3 radial_velocity (primary).
- Sensitivity RV: LAMOST rv (recomputed for sample_final_strict subset only).
- MC = 1000 draws/star.

Inputs
------
- data/processed/hivel_with_bailer_jones_distance.parquet  (1101 rows + flags + BJ)

Outputs
-------
- data/processed/final_kinematics_gaia_only_clean.parquet  (sample_gaia_only_clean ∩ Gaia RV)
- data/processed/final_kinematics_strict.parquet           (sample_final_strict)
- data/processed/final_top_candidates.csv                  (top 30 by P_unbound_final)
- data/processed/final_rv_sensitivity.csv                  (strict, side-by-side Gaia/LAMOST RV)
- reports/final_kinematics_summary.md
"""
from __future__ import annotations
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, PROCESSED_DIR
from caosp_hivel.kinematics import compute_with_distance, monte_carlo_with_distance
from caosp_hivel.log import get_logger

REPORTS_DIR = ROOT / "reports"
N_MC = 1000


def _resolve_distance(row: pd.Series) -> tuple[float, float, float, str]:
    """Return (distance_pc, err_low, err_high, source). BJ if available, else inv-plx."""
    if pd.notna(row.get("bj_r_med_geo")):
        d = float(row["bj_r_med_geo"])
        lo = float(row["bj_distance_err_low"]) if pd.notna(row.get("bj_distance_err_low")) else d * 0.1
        hi = float(row["bj_distance_err_high"]) if pd.notna(row.get("bj_distance_err_high")) else d * 0.1
        return d, lo, hi, "bailer_jones_geo"
    if pd.notna(row.get("parallax")) and row["parallax"] > 0:
        plx = float(row["parallax"])
        plx_err = float(row.get("parallax_error", plx * 0.1))
        d = 1000.0 / plx
        # propagate plx error into distance error linearly
        derr = d * (plx_err / plx)
        return d, derr, derr, "inverse_parallax_fallback"
    return np.nan, np.nan, np.nan, "no_distance"


def _kin_pass(df: pd.DataFrame, *, rv_col: str, rv_err_col: str,
              rng: np.random.Generator) -> pd.DataFrame:
    """Compute point-est + MC kinematics for every row in df, using distance per
    _resolve_distance and the requested RV column. Returns one row per input."""
    rows = []
    for r in tqdm(df.itertuples(index=False), total=len(df), ncols=80):
        d, dlo, dhi, src = _resolve_distance(pd.Series(r._asdict()))
        ra = float(r.ra); dec = float(r.dec)
        pmra = float(r.pmra)
        pmra_e = float(r.pmra_error) if pd.notna(r.pmra_error) else 0.5
        pmdec = float(r.pmdec)
        pmdec_e = float(r.pmdec_error) if pd.notna(r.pmdec_error) else 0.5
        rv_val = getattr(r, rv_col)
        rv = float(rv_val) if pd.notna(rv_val) else np.nan
        rv_err_raw = getattr(r, rv_err_col)
        rv_e = float(rv_err_raw) if pd.notna(rv_err_raw) else 30.0

        k = compute_with_distance(ra, dec, d if np.isfinite(d) else 0.0,
                                  pmra, pmdec, rv if np.isfinite(rv) else 0.0)
        mc = monte_carlo_with_distance(
            ra, dec, d, dlo, dhi,
            pmra, pmra_e, pmdec, pmdec_e, rv, rv_e,
            n=N_MC, rng=rng,
        )
        rows.append({
            "source_id": int(r.source_id),
            "distance_pc": d,
            "distance_err_low": dlo,
            "distance_err_high": dhi,
            "distance_source": src,
            "U": k.U, "V": k.V, "W": k.W,
            "V_total": k.V_total, "V_GSR": k.V_GSR,
            "x_gc": k.x_gc, "y_gc": k.y_gc, "z_gc": k.z_gc, "R_gc": k.R_gc,
            "v_esc": k.v_esc, "v_over_vesc": k.v_ratio,
            "V_total_mc_mean": mc["V_total_mean"],
            "V_total_mc_std":  mc["V_total_std"],
            "V_GSR_mc_mean":   mc["V_GSR_mean"],
            "V_GSR_mc_std":    mc["V_GSR_std"],
            "P_v500":          mc["P_v500"],
            "P_unbound_final": mc["P_unbound"],
            "n_mc_ok":         mc["n_mc"],
        })
    return pd.DataFrame(rows)


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step6b")

    src = PROCESSED_DIR / "hivel_with_bailer_jones_distance.parquet"
    if not src.exists():
        log.error("missing %s — run step 4D first", src)
        return 1
    master = pd.read_parquet(src)
    log.info("master loaded: %d rows", len(master))

    rng = np.random.default_rng(42)

    # ---- pass 1: gaia_only_clean (Gaia RV) ----
    only = master[master["sample_gaia_only_clean"]].reset_index(drop=True)
    log.info("pass A: sample_gaia_only_clean (Gaia RV) — %d rows", len(only))
    t0 = time.time()
    kA = _kin_pass(only, rv_col="radial_velocity", rv_err_col="radial_velocity_error", rng=rng)
    log.info("  done in %.1f s", time.time() - t0)
    only_out = only.merge(kA, on="source_id", how="left", suffixes=("_pre", ""))
    out_only = PROCESSED_DIR / "final_kinematics_gaia_only_clean.parquet"
    only_out.to_parquet(out_only, index=False)
    log.info("  -> %s", out_only)

    # ---- pass 2: strict (Gaia RV) ----
    strict = master[master["sample_final_strict"]].reset_index(drop=True)
    log.info("pass B: sample_final_strict (Gaia RV) — %d rows", len(strict))
    kB = _kin_pass(strict, rv_col="radial_velocity", rv_err_col="radial_velocity_error", rng=rng)
    strict_out = strict.merge(kB, on="source_id", how="left", suffixes=("_pre", ""))
    out_strict = PROCESSED_DIR / "final_kinematics_strict.parquet"
    strict_out.to_parquet(out_strict, index=False)
    log.info("  -> %s", out_strict)

    # ---- pass 3: strict (LAMOST RV) for sensitivity ----
    log.info("pass C: sample_final_strict (LAMOST RV) — %d rows", len(strict))
    kC = _kin_pass(strict, rv_col="lamost_rv", rv_err_col="lamost_rv_err", rng=rng)
    sens = strict[["source_id", "catalogs", "ra", "dec",
                   "radial_velocity", "lamost_rv", "delta_rv"]].copy()
    sens = sens.merge(
        kB[["source_id", "V_GSR", "P_unbound_final"]].rename(
            columns={"V_GSR": "V_GSR_gaia_rv", "P_unbound_final": "P_unbound_gaia_rv"}),
        on="source_id", how="left",
    ).merge(
        kC[["source_id", "V_GSR", "P_unbound_final"]].rename(
            columns={"V_GSR": "V_GSR_lamost_rv", "P_unbound_final": "P_unbound_lamost_rv"}),
        on="source_id", how="left",
    )
    sens["V_GSR_delta"] = sens["V_GSR_lamost_rv"] - sens["V_GSR_gaia_rv"]
    sens["P_unbound_delta"] = sens["P_unbound_lamost_rv"] - sens["P_unbound_gaia_rv"]
    out_sens = PROCESSED_DIR / "final_rv_sensitivity.csv"
    sens.to_csv(out_sens, index=False)
    log.info("  -> %s", out_sens)

    # ---- top candidates from strict (Gaia RV primary) ----
    cand_cols = [
        "source_id", "catalogs",
        "ra", "dec",
        "distance_pc", "distance_source",
        "U", "V", "W",
        "V_total", "V_GSR",
        "v_esc", "v_over_vesc",
        "V_GSR_mc_mean", "V_GSR_mc_std",
        "P_v500", "P_unbound_final",
        "ruwe", "parallax_over_error",
        "radial_velocity", "lamost_rv",
        "lamost_teff", "lamost_logg", "lamost_feh",
        "lamost_designation",
    ]
    keep = [c for c in cand_cols if c in strict_out.columns]
    top = strict_out.sort_values("P_unbound_final", ascending=False).head(30)[keep].copy()
    # Force source_id to string so downstream readers cannot accidentally
    # parse it as float64 (which would lose ~3 trailing digits of a 19-digit id).
    top["source_id"] = top["source_id"].astype("int64").astype(str)
    out_top = PROCESSED_DIR / "final_top_candidates.csv"
    top.to_csv(out_top, index=False)
    log.info("  top-30 -> %s", out_top)

    # ---------- report ----------
    n_strict = len(strict)
    n_only = len(only)
    n_bj_strict = int((strict_out["distance_source"] == "bailer_jones_geo").sum())
    n_fallback_strict = int((strict_out["distance_source"] == "inverse_parallax_fallback").sum())
    n_unb05 = int((strict_out["P_unbound_final"] > 0.5).sum())
    n_unb09 = int((strict_out["P_unbound_final"] > 0.9).sum())

    md = []
    md.append("# Final kinematics report (Step 6B)\n")
    md.append(f"Generated by `scripts/06B_final_kinematics.py`. MC = {N_MC} draws/star.\n")

    md.append("## 1. Conventions\n")
    md.append("- Default distance: **Bailer-Jones (2021) `r_med_geo`** "
              "(`external.gaiaedr3_distance`).")
    md.append("- Fallback distance: `1000 / parallax` with `distance_source = inverse_parallax_fallback`.")
    md.append("- Distance MC: log-normal from BJ 16th/84th percentiles (or 10% Gaussian for fallback).")
    md.append("- Primary RV: **Gaia DR3 `radial_velocity`**. Sensitivity: **LAMOST `rv`** "
              "(strict subset only).")
    md.append("- Galactic potential: galpy `MWPotential2014`. v_esc evaluated in-plane (z=0).\n")

    md.append("## 2. Sample sizes\n")
    md.append("| sample | N | BJ distance | inv-plx fallback |")
    md.append("|---|---:|---:|---:|")
    md.append(f"| sample_gaia_only_clean | {n_only} | "
              f"{int((only_out['distance_source']=='bailer_jones_geo').sum())} | "
              f"{int((only_out['distance_source']=='inverse_parallax_fallback').sum())} |")
    md.append(f"| sample_final_strict | {n_strict} | {n_bj_strict} | {n_fallback_strict} |")
    md.append("")

    md.append("## 3. Final-strict velocity / unbound counts (Gaia RV primary)\n")
    md.append("| filter | count |")
    md.append("|---|---:|")
    md.append(f"| V_GSR > 500 km/s (point) | "
              f"{int((strict_out['V_GSR'] > 500).sum())} |")
    md.append(f"| P_unbound_final > 0.5 | {n_unb05} |")
    md.append(f"| P_unbound_final > 0.9 | {n_unb09} |")
    md.append("")

    md.append("## 4. Top-30 final candidates (Gaia RV primary)\n")
    md.append("| rank | source_id | catalogs | dist (pc) | V_GSR | V_GSR ± std | P_unbound | "
              "Teff | logg | [Fe/H] |")
    md.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for i, (_, r) in enumerate(top.iterrows(), 1):
        md.append(
            f"| {i} | {int(r['source_id'])} | {r.get('catalogs','')} | "
            f"{r['distance_pc']:.0f} | {r['V_GSR']:.0f} | "
            f"{r.get('V_GSR_mc_mean', float('nan')):.0f} ± {r.get('V_GSR_mc_std', float('nan')):.0f} | "
            f"{r['P_unbound_final']:.3f} | "
            f"{(r.get('lamost_teff') or float('nan')):.0f} | "
            f"{(r.get('lamost_logg') or float('nan')):.2f} | "
            f"{(r.get('lamost_feh')  or float('nan')):.2f} |"
        )
    md.append("")

    md.append("## 5. RV sensitivity (LAMOST RV vs Gaia RV) on `sample_final_strict`\n")
    if not sens.empty:
        dV = sens["V_GSR_delta"].dropna()
        dP = sens["P_unbound_delta"].dropna()
        md.append(f"- N: {len(sens)}")
        md.append(f"- median ΔV_GSR (LAMOST − Gaia): **{float(dV.median()):.2f} km/s**")
        md.append(f"- p90 |ΔV_GSR|: {float(dV.abs().quantile(0.9)):.2f} km/s")
        md.append(f"- max |ΔV_GSR|: {float(dV.abs().max()):.2f} km/s")
        md.append(f"- median ΔP_unbound (LAMOST − Gaia): {float(dP.median()):.3f}")
        md.append(f"- N stars whose P_unbound flips across 0.5: "
                  f"{int(((sens['P_unbound_gaia_rv']>0.5) ^ (sens['P_unbound_lamost_rv']>0.5)).sum())}")
        md.append(f"- Output: `{out_sens.relative_to(ROOT)}`")
    md.append("")

    md.append("## 6. Comparison to Step 4B preliminary Top-50\n")
    pre_top = PROCESSED_DIR / "top_unbound_candidates.csv"
    if pre_top.exists():
        pre = pd.read_csv(pre_top)
        merged = pre[["source_id", "P_unbound"]].rename(columns={"P_unbound": "P_unbound_pre"}) \
            .merge(strict_out[["source_id", "P_unbound_final", "distance_source"]],
                   on="source_id", how="left")
        n_in_strict = int(merged["P_unbound_final"].notna().sum())
        n_kept_high = int((merged["P_unbound_final"] > 0.5).sum())
        n_dropped_dist = int(((merged["P_unbound_pre"] > 0.5) &
                              (merged["P_unbound_final"] <= 0.5)).sum())
        md.append(f"- Preliminary Top-50 also in `sample_final_strict`: **{n_in_strict}**")
        md.append(f"- Of those, P_unbound_final > 0.5 (still high-conf after BJ): **{n_kept_high}**")
        md.append(f"- Dropped below 0.5 due to BJ distance shrinkage: **{n_dropped_dist}**")
        md.append("")

    md.append("## 7. Recommended sample for the paper\n")
    md.append("- **Primary kinematic results**: `sample_final_strict` + Bailer-Jones distance "
              "+ Gaia DR3 RV. This is the population for Table 3 and Section 4.2 of the paper.")
    md.append("- **LAMOST RV pass**: a sensitivity check (median ΔV_GSR is small); not the headline number.")
    md.append("- **Background distributions (Toomre, Galactic-coord scatter)**: "
              "`sample_gaia_only_clean` + BJ distance.")
    md.append("- **RV outliers (3 stars in master, 2 in followup)**: kept as "
              "\"possible binaries / variable-RV objects requiring follow-up spectroscopy\". "
              "Excluded from the headline Table 3.")
    md.append("- **li2023 caveat**: The Li et al. 2023 very-high-velocity subset is retained in "
              "the Gaia-only analysis, but none of its 88 objects enters the final Gaia–LAMOST "
              "strict sample under our S/N and cross-match criteria. Conclusions involving "
              "atmospheric parameters are therefore based primarily on the Li et al. 2021 and "
              "Liao et al. 2024 subsets.")
    md.append("")

    md.append("## 8. Outputs\n")
    md.append(f"- `{out_only.relative_to(ROOT)}`")
    md.append(f"- `{out_strict.relative_to(ROOT)}`")
    md.append(f"- `{out_top.relative_to(ROOT)}`")
    md.append(f"- `{out_sens.relative_to(ROOT)}`")
    md.append("")

    out_md = REPORTS_DIR / "final_kinematics_summary.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)

    print(f"\nFinal: strict={n_strict}, BJ={n_bj_strict}, "
          f"P_unbound>0.5: {n_unb05}, >0.9: {n_unb09}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
