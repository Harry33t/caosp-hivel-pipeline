"""Step 6E: LAMOST radial-velocity zero-point correction (CAOSP referee).

Referee's request:
   "The manuscript mentions a known zero-point offset in LAMOST radial
    velocities but does not apply corrections. Recommendation: apply
    the correction or provide a more rigorous justification."

Step 5 measured the median offset on our matched subset:
   median (LAMOST - Gaia)_RV = -5.66 km/s
                            == LAMOST is systematically lower than Gaia.

We therefore apply LAMOST_corrected = LAMOST_raw + 5.66 km/s, re-run
the kinematic Monte Carlo on the same 356-star final-strict sample,
and report whether the unbound classification changes.

Inputs:  data/processed/final_kinematics_strict.parquet
         data/processed/final_rv_sensitivity.csv   (raw vs Gaia)
Outputs: data/processed/lamost_rv_zeropoint_check.csv
         reports/lamost_rv_zeropoint.md
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

# Median LAMOST-Gaia offset measured in Step 5 on the matched subset.
LAMOST_ZEROPOINT_KMS = 5.66   # add this to LAMOST RV to align with Gaia frame


def _resolve_distance(row: pd.Series) -> tuple[float, float, float]:
    d = float(row["distance_pc"])
    lo = float(row["distance_err_low"]) if pd.notna(row["distance_err_low"]) else d * 0.1
    hi = float(row["distance_err_high"]) if pd.notna(row["distance_err_high"]) else d * 0.1
    return d, lo, hi


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step6e")

    src = PROCESSED_DIR / "final_kinematics_strict.parquet"
    if not src.exists():
        log.error("missing %s -- run Step 6B first", src)
        return 1
    df = pd.read_parquet(src)
    log.info("final-strict: %d stars; applying LAMOST RV zero-point of "
             "+%.2f km/s to LAMOST radial velocities", len(df), LAMOST_ZEROPOINT_KMS)

    rng = np.random.default_rng(20260910)
    rows = []
    t0 = time.time()
    for r in tqdm(df.itertuples(index=False), total=len(df), ncols=80):
        d, dlo, dhi = _resolve_distance(pd.Series(r._asdict()))
        ra, dec   = float(r.ra), float(r.dec)
        pmra      = float(r.pmra)
        pmra_e    = float(r.pmra_error)  if pd.notna(r.pmra_error)  else 0.5
        pmdec     = float(r.pmdec)
        pmdec_e   = float(r.pmdec_error) if pd.notna(r.pmdec_error) else 0.5

        rv_lamost_raw = float(r.lamost_rv) if pd.notna(r.lamost_rv) else np.nan
        rv_lamost_e   = float(r.lamost_rv_err) if pd.notna(r.lamost_rv_err) else 30.0

        # zero-point-corrected LAMOST RV
        rv_lamost_zp = rv_lamost_raw + LAMOST_ZEROPOINT_KMS \
                       if np.isfinite(rv_lamost_raw) else np.nan

        mc = monte_carlo_with_distance(
            ra, dec, d, dlo, dhi,
            pmra, pmra_e, pmdec, pmdec_e,
            rv_lamost_zp, rv_lamost_e,
            n=N_MC, rng=rng,
        )
        rows.append({
            "source_id": int(r.source_id),
            "lamost_rv_raw":      rv_lamost_raw,
            "lamost_rv_corrected": rv_lamost_zp,
            "V_GSR_lamostZP_mc_mean": mc["V_GSR_mean"],
            "V_GSR_lamostZP_mc_std":  mc["V_GSR_std"],
            "P_unbound_lamostZP":     mc["P_unbound"],
        })

    log.info("MC done in %.1f s", time.time() - t0)

    zp = pd.DataFrame(rows)
    zp["source_id"] = zp["source_id"].astype("int64").astype(str)

    # merge against the prior Gaia-RV / raw-LAMOST-RV results from Step 6B
    sens_path = PROCESSED_DIR / "final_rv_sensitivity.csv"
    sens = pd.read_csv(sens_path, dtype={"source_id": str})
    merged = sens.merge(zp, on="source_id", how="left")
    merged["delta_V_lamostZP_minus_gaia"] = (
        merged["V_GSR_lamostZP_mc_mean"] - merged["V_GSR_gaia_rv"]
    )

    out_csv = PROCESSED_DIR / "lamost_rv_zeropoint_check.csv"
    merged.to_csv(out_csv, index=False)
    log.info("CSV -> %s", out_csv)

    # ---- summary statistics on the same 356 stars ----
    n = len(merged)
    n_gaia05    = int((merged["P_unbound_gaia_rv"]    > 0.5).sum())
    n_lamost05  = int((merged["P_unbound_lamost_rv"]  > 0.5).sum())
    n_lamostZP05= int((merged["P_unbound_lamostZP"]   > 0.5).sum())
    n_gaia09    = int((merged["P_unbound_gaia_rv"]    > 0.9).sum())
    n_lamost09  = int((merged["P_unbound_lamost_rv"]  > 0.9).sum())
    n_lamostZP09= int((merged["P_unbound_lamostZP"]   > 0.9).sum())

    dV = merged["delta_V_lamostZP_minus_gaia"].dropna()
    flips_05_lamost   = int(((merged["P_unbound_gaia_rv"] > 0.5) ^
                             (merged["P_unbound_lamost_rv"] > 0.5)).sum())
    flips_05_lamostZP = int(((merged["P_unbound_gaia_rv"] > 0.5) ^
                             (merged["P_unbound_lamostZP"] > 0.5)).sum())

    md = []
    md.append("# LAMOST RV zero-point sensitivity check (Step 6E)\n")
    md.append("Per the Step 5 cross-match, the median offset between LAMOST\n"
              "DR9 LRS radial velocities and Gaia DR3 radial velocities on\n"
              "the matched subset is\n")
    md.append("$$\\mathrm{median}(v_{\\rm RV,LAMOST} - v_{\\rm RV,Gaia})"
              f" = -{LAMOST_ZEROPOINT_KMS:.2f}\\;\\mathrm{{km\\,s^{{-1}}}}.$$\n")
    md.append(f"This step adds **+{LAMOST_ZEROPOINT_KMS:.2f} km/s** to every "
              "LAMOST radial velocity to align it with the Gaia frame, then "
              "recomputes the kinematic solution on the same 356-star "
              "final-strict sample with 1000-draw Monte Carlo error "
              "propagation under MWPotential2014.\n")

    md.append("## Unbound counts on the same 356-star sample\n")
    md.append("| threshold | Gaia RV (primary) | LAMOST RV raw | LAMOST RV zero-point corrected |")
    md.append("|---|---:|---:|---:|")
    md.append(f"| $P_{{\\rm unbound}} > 0.5$ | {n_gaia05} | {n_lamost05} | **{n_lamostZP05}** |")
    md.append(f"| $P_{{\\rm unbound}} > 0.9$ | {n_gaia09} | {n_lamost09} | **{n_lamostZP09}** |")
    md.append("")

    md.append("## Per-star reclassification across $P_{\\rm unbound} = 0.5$\n")
    md.append("| comparison | stars whose 0.5 classification flips |")
    md.append("|---|---:|")
    md.append(f"| Gaia RV vs LAMOST RV (raw)               | {flips_05_lamost} |")
    md.append(f"| Gaia RV vs LAMOST RV (zero-point corrected) | **{flips_05_lamostZP}** |")
    md.append("")

    md.append("## $V_{\\rm GSR}$ shift induced by the +5.66 km/s correction\n")
    if len(dV):
        md.append(f"- N: {len(dV)}")
        md.append(f"- median $\\Delta V_{{\\rm GSR}}$ (LAMOST-corrected $-$ Gaia): "
                  f"**{float(dV.median()):.2f} km/s**")
        md.append(f"- $p_{{90}} |\\Delta V_{{\\rm GSR}}|$: "
                  f"{float(dV.abs().quantile(0.9)):.2f} km/s")
        md.append(f"- max $|\\Delta V_{{\\rm GSR}}|$: {float(dV.abs().max()):.2f} km/s")
    md.append("")

    md.append("## Conclusion (suggested phrasing for the manuscript)\n")
    if n_lamostZP05 == n_lamost05 and flips_05_lamostZP <= flips_05_lamost + 1:
        md.append("> Applying a +5.66 km/s zero-point correction to the LAMOST "
                  "radial velocities (the median offset measured against Gaia "
                  "DR3 on the matched subset; Sect.\\ ?) does not change the "
                  "unbound classification of the final-strict sample by more "
                  "than one star. The headline reduction from 48 to 3 "
                  "(distance) is therefore not affected by the LAMOST "
                  "zero-point.")
    else:
        md.append("> Applying a +5.66 km/s zero-point correction to the LAMOST "
                  "radial velocities changes the count of stars with "
                  f"$P_{{\\rm unbound}}>0.5$ from {n_lamost05} (raw) to "
                  f"{n_lamostZP05} (corrected). This shift is small compared "
                  "with the 48-to-3 reduction induced by the distance "
                  "estimator, but is reported here for completeness.")
    md.append("")

    md.append("## Output\n")
    md.append(f"- `{out_csv.relative_to(ROOT)}`")
    md.append("")

    out_md = REPORTS_DIR / "lamost_rv_zeropoint.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)

    print(f"\nFinal-strict N={n}, MC={N_MC}")
    print(f"  P_unb>0.5: GaiaRV={n_gaia05}, LAMOST raw={n_lamost05}, "
          f"LAMOST +ZP={n_lamostZP05}")
    print(f"  P_unb>0.9: GaiaRV={n_gaia09}, LAMOST raw={n_lamost09}, "
          f"LAMOST +ZP={n_lamostZP09}")
    print(f"  flips across 0.5 vs Gaia: raw={flips_05_lamost}, "
          f"+ZP={flips_05_lamostZP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
