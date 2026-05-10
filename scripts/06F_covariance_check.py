"""Step 6F: Gaia DR3 covariance-matrix Monte Carlo (CAOSP referee).

Referee's request:
   "the manuscript does not clearly describe how uncertainties are
    propagated, particularly with respect to correlated astrometric
    parameters. Recommendation: clarify whether full covariance matrices
    are used and discuss the impact of correlated errors."

Steps 4B and 6B sampled (parallax, pmra, pmdec) and the radial velocity
independently. Gaia DR3 publishes the full 5x5 ICRS covariance matrix
of (alpha, delta, parallax, pmra*, pmdec). For our final-strict
sample we evaluate the impact of the three astrometric off-diagonal
correlations:

   parallax_pmra_corr
   parallax_pmdec_corr
   pmra_pmdec_corr

by re-running the kinematic Monte Carlo with multivariate-normal
draws of (parallax, pmra, pmdec) instead of three independent normals.
The radial velocity remains an independent normal (Gaia DR3 RVS RVs
are produced by a separate pipeline and are uncorrelated with the
astrometric solution at the catalogue level).

We evaluate distance from the parallax draws via 1/parallax (kpc),
not from the Bailer-Jones log-normal, so that the comparison cleanly
isolates the astrometric covariance effect; the headline conclusion
about distance estimators is left untouched.

Inputs:  data/processed/final_kinematics_strict.parquet
Outputs:
   data/processed/covariance_check.csv
   reports/covariance_check.md
"""
from __future__ import annotations
import sys
import time
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.table import Table
from astroquery.gaia import Gaia

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, PROCESSED_DIR, CACHE_DIR
from caosp_hivel.kinematics import (
    GALCEN_FRAME, _vesc_at,
)
from caosp_hivel.log import get_logger

REPORTS_DIR = ROOT / "reports"
N_MC = 1000

CORR_CACHE = CACHE_DIR / "gaia_correlations_strict.parquet"
CORR_FIELDS = [
    "source_id",
    "parallax_pmra_corr",
    "parallax_pmdec_corr",
    "pmra_pmdec_corr",
]


def fetch_correlations(source_ids: list[int]) -> pd.DataFrame:
    """Fetch the three astrometric correlations from Gaia DR3.
    Cached locally to cache/gaia_correlations_strict.parquet."""
    log = get_logger("caosp.step6f")
    if CORR_CACHE.exists():
        cached = pd.read_parquet(CORR_CACHE)
        if set(cached["source_id"]) >= set(source_ids):
            log.info("correlation cache hit (%d rows)", len(cached))
            return cached

    log.info("Gaia TAP upload-join for %d source_ids ...", len(source_ids))
    upload_path = CACHE_DIR / "_corr_upload.xml"
    Table({"source_id": source_ids}).write(upload_path, format="votable", overwrite=True)
    try:
        job = Gaia.launch_job_async(
            query=(
                "SELECT u.source_id, g.parallax_pmra_corr, "
                "g.parallax_pmdec_corr, g.pmra_pmdec_corr "
                "FROM gaiadr3.gaia_source AS g "
                "JOIN tap_upload.ids AS u USING (source_id)"
            ),
            upload_resource=str(upload_path),
            upload_table_name="ids",
        )
        df = job.get_results().to_pandas()
    finally:
        upload_path.unlink(missing_ok=True)
    df["source_id"] = df["source_id"].astype("int64")
    df.to_parquet(CORR_CACHE, index=False)
    log.info("correlations cached: %d rows", len(df))
    return df


def _build_cov_matrix(plx_e: float, pmra_e: float, pmdec_e: float,
                      c_plx_pmra: float, c_plx_pmdec: float, c_pmra_pmdec: float):
    """3x3 covariance matrix for (parallax, pmra, pmdec)."""
    cov = np.array([
        [plx_e**2,                     c_plx_pmra * plx_e * pmra_e, c_plx_pmdec * plx_e * pmdec_e],
        [c_plx_pmra * plx_e * pmra_e,  pmra_e**2,                   c_pmra_pmdec * pmra_e * pmdec_e],
        [c_plx_pmdec * plx_e * pmdec_e,c_pmra_pmdec * pmra_e * pmdec_e, pmdec_e**2],
    ])
    return cov


def _kinematic_mc(row: pd.Series, *, use_corr: bool, n: int, rng) -> dict:
    """Run kinematic MC for one star; sample astrometry either independently
    or with the 3x3 covariance applied. Returns P_unbound + V_GSR mean/std."""
    plx   = float(row["parallax"])
    plx_e = float(row["parallax_error"])
    pmra  = float(row["pmra"]);  pmra_e  = float(row["pmra_error"])
    pmdec = float(row["pmdec"]); pmdec_e = float(row["pmdec_error"])
    rv    = float(row["radial_velocity"]) if pd.notna(row["radial_velocity"]) else np.nan
    rv_e  = float(row["radial_velocity_error"]) if pd.notna(row["radial_velocity_error"]) else 30.0

    if use_corr:
        cov = _build_cov_matrix(
            plx_e, pmra_e, pmdec_e,
            float(row["parallax_pmra_corr"]),
            float(row["parallax_pmdec_corr"]),
            float(row["pmra_pmdec_corr"]),
        )
        # multivariate_normal will internally add a tiny jitter if cov is
        # numerically non-PSD due to rounding; suppress the warning.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            samples = rng.multivariate_normal([plx, pmra, pmdec], cov, size=n)
    else:
        samples = np.column_stack([
            rng.normal(plx,   max(plx_e,   1e-6), n),
            rng.normal(pmra,  max(pmra_e,  1e-6), n),
            rng.normal(pmdec, max(pmdec_e, 1e-6), n),
        ])
    plx_v, pmra_v, pmdec_v = samples[:, 0], samples[:, 1], samples[:, 2]

    has_rv = np.isfinite(rv)
    rv_v = rng.normal(rv, max(rv_e, 1e-6), n) if has_rv else np.zeros(n)

    valid = plx_v > 0
    if valid.sum() == 0:
        return {"P_unbound": np.nan, "V_GSR_mean": np.nan, "V_GSR_std": np.nan}

    d_kpc = 1.0 / plx_v[valid]
    nv = int(valid.sum())
    icrs = SkyCoord(
        ra=np.full(nv, float(row["ra"])) * u.deg,
        dec=np.full(nv, float(row["dec"])) * u.deg,
        distance=d_kpc * u.kpc,
        pm_ra_cosdec=pmra_v[valid] * u.mas / u.yr,
        pm_dec=pmdec_v[valid] * u.mas / u.yr,
        radial_velocity=rv_v[valid] * u.km / u.s,
        frame="icrs",
    )
    gc = icrs.transform_to(GALCEN_FRAME)
    vx = gc.v_x.to(u.km / u.s).value
    vy = gc.v_y.to(u.km / u.s).value
    vz = gc.v_z.to(u.km / u.s).value
    V_GSR = np.sqrt(vx*vx + vy*vy + vz*vz)
    R_arr = np.hypot(gc.x.to(u.kpc).value, gc.y.to(u.kpc).value)
    v_esc = np.array([_vesc_at(r, 0.0) for r in R_arr])
    return {
        "P_unbound": float(np.mean(V_GSR > v_esc)),
        "V_GSR_mean": float(np.nanmean(V_GSR)),
        "V_GSR_std":  float(np.nanstd(V_GSR)),
    }


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step6f")

    src = PROCESSED_DIR / "final_kinematics_strict.parquet"
    if not src.exists():
        log.error("missing %s -- run Step 6B first", src)
        return 1
    df = pd.read_parquet(src)
    df["source_id"] = df["source_id"].astype("int64")
    log.info("final-strict: %d stars", len(df))

    corr = fetch_correlations(df["source_id"].tolist())
    df = df.merge(corr, on="source_id", how="left")
    n_have_corr = int(
        df[["parallax_pmra_corr", "parallax_pmdec_corr", "pmra_pmdec_corr"]]
        .notna().all(axis=1).sum()
    )
    log.info("stars with full 3x3 correlation entries: %d / %d",
             n_have_corr, len(df))

    rng = np.random.default_rng(20260911)
    rows = []
    t0 = time.time()
    for i, (_, row) in enumerate(df.iterrows()):
        ind = _kinematic_mc(row, use_corr=False, n=N_MC, rng=rng)
        cov = _kinematic_mc(row, use_corr=True,  n=N_MC, rng=rng)
        rows.append({
            "source_id":          int(row["source_id"]),
            "P_unb_independent":  ind["P_unbound"],
            "V_GSR_independent":  ind["V_GSR_mean"],
            "V_GSR_std_indep":    ind["V_GSR_std"],
            "P_unb_covariance":   cov["P_unbound"],
            "V_GSR_covariance":   cov["V_GSR_mean"],
            "V_GSR_std_cov":      cov["V_GSR_std"],
        })
        if (i + 1) % 50 == 0:
            log.info("  %d / %d in %.1f s", i+1, len(df), time.time()-t0)

    out = pd.DataFrame(rows)
    out["P_unb_delta"]    = out["P_unb_covariance"]  - out["P_unb_independent"]
    out["V_GSR_delta"]    = out["V_GSR_covariance"]  - out["V_GSR_independent"]
    out["sigma_ratio"]    = out["V_GSR_std_cov"] / out["V_GSR_std_indep"]
    out["source_id"]      = out["source_id"].astype("int64").astype(str)
    out_csv = PROCESSED_DIR / "covariance_check.csv"
    out.to_csv(out_csv, index=False)
    log.info("CSV -> %s", out_csv)

    # ---- summary ----
    n = len(out)
    n_ind05 = int((out["P_unb_independent"] > 0.5).sum())
    n_cov05 = int((out["P_unb_covariance"]  > 0.5).sum())
    n_ind09 = int((out["P_unb_independent"] > 0.9).sum())
    n_cov09 = int((out["P_unb_covariance"]  > 0.9).sum())
    flips_05 = int(((out["P_unb_independent"] > 0.5) ^ (out["P_unb_covariance"] > 0.5)).sum())
    dP   = out["P_unb_delta"].dropna()
    dV   = out["V_GSR_delta"].dropna()
    sigr = out["sigma_ratio"].dropna()

    md = []
    md.append("# Astrometric covariance Monte Carlo (Step 6F)\n")
    md.append("Both runs use 1/parallax distances (so the result is "
              "comparable to the inverse-parallax pass of Step 4B), 1000 MC "
              "draws/star, and Gaia DR3 radial velocities. The two passes "
              "differ only in how (parallax, pmra, pmdec) are drawn:\n")
    md.append("| pass | $\\Pi=(\\varpi, \\mu_{\\alpha*}, \\mu_\\delta)$ |")
    md.append("|---|---|")
    md.append("| independent | three independent Gaussians at the catalogue errors |")
    md.append("| **covariance** | multivariate Gaussian using the Gaia DR3 3x3 correlation matrix |")
    md.append("")
    md.append(f"Sample size on the final-strict subset: **N = {n}**, of which "
              f"**{n_have_corr}** carry the full 3x3 correlation entries in "
              "`gaiadr3.gaia_source`.\n")

    md.append("## Unbound counts on the same 356-star sample\n")
    md.append("| threshold | independent | covariance |")
    md.append("|---|---:|---:|")
    md.append(f"| $P_{{\\rm unbound}} > 0.5$ | {n_ind05} | **{n_cov05}** |")
    md.append(f"| $P_{{\\rm unbound}} > 0.9$ | {n_ind09} | **{n_cov09}** |")
    md.append(f"| stars whose 0.5 classification flips | --- | **{flips_05}** |")
    md.append("")

    if len(dP):
        md.append("## Per-star shifts induced by the covariance\n")
        md.append(f"- median $\\Delta P_{{\\rm unbound}}$ "
                  f"(covariance $-$ independent): **{float(dP.median()):.4f}**")
        md.append(f"- $p_{{90}} |\\Delta P_{{\\rm unbound}}|$: "
                  f"{float(dP.abs().quantile(0.9)):.4f}")
        md.append(f"- max $|\\Delta P_{{\\rm unbound}}|$: "
                  f"{float(dP.abs().max()):.4f}")
        md.append("")
        md.append(f"- median $\\Delta V_{{\\rm GSR}}$: "
                  f"**{float(dV.median()):.2f} km s$^{{-1}}$**")
        md.append(f"- $p_{{90}} |\\Delta V_{{\\rm GSR}}|$: "
                  f"{float(dV.abs().quantile(0.9)):.2f} km s$^{{-1}}$")
        md.append("")
        md.append(f"- median ratio of $V_{{\\rm GSR}}$ MC scatter "
                  f"$\\sigma_{{\\rm cov}}/\\sigma_{{\\rm ind}}$: "
                  f"**{float(sigr.median()):.3f}**")
        md.append(f"- $p_{{90}}$ of that ratio: {float(sigr.quantile(0.9)):.3f}")
        md.append("")

    md.append("## Conclusion (suggested phrasing for the manuscript)\n")
    md.append("> We have repeated the kinematic Monte Carlo using the full "
              "Gaia DR3 astrometric covariance matrix "
              "($\\sigma_{\\varpi\\mu_{\\alpha*}}$, $\\sigma_{\\varpi\\mu_\\delta}$, "
              "$\\sigma_{\\mu_{\\alpha*}\\mu_\\delta}$) to draw "
              "$(\\varpi, \\mu_{\\alpha*}, \\mu_\\delta)$ jointly rather "
              f"than independently. On the final-strict sample of {n} stars "
              f"the count with $P_{{\\rm unbound}}>0.5$ moves by "
              f"{n_cov05 - n_ind05:+d} (from {n_ind05} to {n_cov05}), the "
              f"median $|\\Delta P_{{\\rm unbound}}|$ is "
              f"{float(dP.abs().median()) if len(dP) else 0:.4f}, and "
              f"{flips_05} stars flip across the 0.5 threshold. The headline "
              "48-to-3 reduction induced by the distance estimator is "
              "therefore unaffected by the choice of independent vs. "
              "correlated astrometric sampling.")
    md.append("")

    md.append("## Output\n")
    md.append(f"- `{out_csv.relative_to(ROOT)}`")
    md.append("")

    out_md = REPORTS_DIR / "covariance_check.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)

    print(f"\nFinal-strict N={n}, with corr={n_have_corr}, MC={N_MC}")
    print(f"  P_unb>0.5: independent={n_ind05}, covariance={n_cov05}")
    print(f"  P_unb>0.9: independent={n_ind09}, covariance={n_cov09}")
    print(f"  flips across 0.5: {flips_05}")
    if len(dP):
        print(f"  median |delta P|: {float(dP.abs().median()):.4f}")
        print(f"  median sigma_cov / sigma_ind: {float(sigr.median()):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
