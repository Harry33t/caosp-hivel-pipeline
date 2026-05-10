"""Step 6D: Galactic-potential robustness check (CAOSP referee request).

Re-runs the unbound classification on the *same* final-strict 356-star
sample under three independently-published Milky-Way potentials:

  - MWPotential2014  (Bovy 2015)
  - McMillan17        (McMillan 2017, MNRAS 465, 76)
  - Irrgang13I        (Irrgang et al. 2013 model I)

For each potential, the local escape speed v_esc is recomputed from
the potential's own (R0, V0) units, and P_unbound = P(v_grf > v_esc)
is re-evaluated by Monte Carlo (N=1000 per star).

Inputs:  data/processed/final_kinematics_strict.parquet
Outputs:
  data/processed/potential_robustness.csv
  reports/potential_robustness.md
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
from galpy.potential import MWPotential2014, vesc as galpy_vesc
from galpy.potential.mwpotentials import McMillan17, Irrgang13I

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, PROCESSED_DIR
from caosp_hivel.kinematics import (
    R_SUN_KPC, Z_SUN_KPC, V_SUN_GAL, GALCEN_FRAME,
)
from caosp_hivel.log import get_logger

REPORTS_DIR = ROOT / "reports"
N_MC = 500   # 500 draws keeps runtime ~3 min for 356 stars * 3 potentials


# Each potential needs its own (R0, V0) to convert galpy natural units to km/s.
POTS = {
    "MWPotential2014": {"pot": MWPotential2014, "R0": 8.0,  "V0": 220.0},
    "McMillan17":      {"pot": McMillan17,      "R0": 8.21, "V0": 233.1},
    "Irrgang13I":      {"pot": Irrgang13I,      "R0": 8.4,  "V0": 242.0},
}


def _build_vesc_grid(pot, R0: float, V0: float, n_grid: int = 200):
    """Precompute v_esc(R) on a 0.5 - 50 kpc log grid; return an
    interpolator that takes R [kpc] and returns v_esc [km/s].

    McMillan17 is a CompositePotential including a DiskSCFPotential, so
    a single galpy_vesc call costs ~0.05 s. Doing this 500*356*3 times
    is hours; precomputing 200 grid points and interpolating is sub-second.
    """
    R_grid_kpc = np.geomspace(0.5, 50.0, n_grid)
    v = np.zeros_like(R_grid_kpc)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i, R in enumerate(R_grid_kpc):
            v[i] = float(galpy_vesc(pot, R / R0)) * V0

    def interpolate(R_arr_kpc):
        return np.interp(np.clip(R_arr_kpc, 0.5, 50.0),
                         R_grid_kpc, v)
    return interpolate


def _sample_kinematics_for_star(row, *, n: int, rng) -> tuple[np.ndarray, np.ndarray]:
    """Return (V_GSR samples in km/s, R_gc samples in kpc) for one star.
    Uses BJ distance log-normal sampling and independent astrometry/RV
    Gaussian sampling. Returns only the finite ones."""
    d_med = float(row["distance_pc"])
    d_lo  = float(row["distance_err_low"])
    d_hi  = float(row["distance_err_high"])
    sigma_log = (np.log10(d_med + d_hi) - np.log10(max(d_med - d_lo, 1e-3))) / 2.0
    d_s = np.power(10.0, rng.normal(np.log10(d_med), max(sigma_log, 1e-4), n))

    pmra_e   = float(row["pmra_error"])   if pd.notna(row["pmra_error"])   else 0.5
    pmdec_e  = float(row["pmdec_error"])  if pd.notna(row["pmdec_error"])  else 0.5
    rv_e     = float(row["radial_velocity_error"]) \
        if pd.notna(row["radial_velocity_error"]) else 30.0

    pmra_v   = rng.normal(float(row["pmra"]),   max(pmra_e, 1e-6),  n)
    pmdec_v  = rng.normal(float(row["pmdec"]),  max(pmdec_e, 1e-6), n)
    rv       = float(row["radial_velocity"]) if pd.notna(row["radial_velocity"]) else 0.0
    rv_v     = rng.normal(rv, max(rv_e, 1e-6), n)

    valid = d_s > 0
    d_v   = d_s[valid]
    pmra_v   = pmra_v[valid]
    pmdec_v  = pmdec_v[valid]
    rv_v     = rv_v[valid]
    nv = len(d_v)
    if nv == 0:
        return np.array([]), np.array([])

    icrs = SkyCoord(
        ra=np.full(nv, float(row["ra"])) * u.deg,
        dec=np.full(nv, float(row["dec"])) * u.deg,
        distance=(d_v / 1000.0) * u.kpc,
        pm_ra_cosdec=pmra_v * u.mas / u.yr,
        pm_dec=pmdec_v * u.mas / u.yr,
        radial_velocity=rv_v * u.km / u.s,
        frame="icrs",
    )
    gc = icrs.transform_to(GALCEN_FRAME)
    vx = gc.v_x.to(u.km / u.s).value
    vy = gc.v_y.to(u.km / u.s).value
    vz = gc.v_z.to(u.km / u.s).value
    V_GSR = np.sqrt(vx*vx + vy*vy + vz*vz)
    R_gc  = np.hypot(gc.x.to(u.kpc).value, gc.y.to(u.kpc).value)
    return V_GSR, R_gc


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step6d")

    src = PROCESSED_DIR / "final_kinematics_strict.parquet"
    if not src.exists():
        log.error("missing %s -- run Step 6B first", src)
        return 1
    df = pd.read_parquet(src)
    log.info("final-strict sample: %d stars", len(df))

    log.info("precomputing v_esc(R) grids for 3 potentials ...")
    t0 = time.time()
    vesc_funcs = {
        name: _build_vesc_grid(p["pot"], p["R0"], p["V0"])
        for name, p in POTS.items()
    }
    log.info("  done in %.1f s", time.time() - t0)

    rng = np.random.default_rng(20260909)
    rows = []
    t1 = time.time()
    for i, (_, row) in enumerate(df.iterrows()):
        V_GSR, R_gc = _sample_kinematics_for_star(row, n=N_MC, rng=rng)
        if len(V_GSR) == 0:
            rows.append({"source_id": int(row["source_id"]),
                         "P_unb_MWPotential2014": np.nan,
                         "P_unb_McMillan17":      np.nan,
                         "P_unb_Irrgang13I":      np.nan})
            continue

        out = {"source_id": int(row["source_id"])}
        for name, fn in vesc_funcs.items():
            v_esc = fn(R_gc)
            out[f"P_unb_{name}"] = float(np.mean(V_GSR > v_esc))
        rows.append(out)
        if (i + 1) % 50 == 0:
            log.info("  %d / %d stars in %.1f s", i+1, len(df), time.time()-t1)

    log.info("MC over 3 potentials: %.1f s", time.time() - t0)

    rob = pd.DataFrame(rows)
    rob["source_id"] = rob["source_id"].astype("int64").astype(str)
    out_csv = PROCESSED_DIR / "potential_robustness.csv"
    rob.to_csv(out_csv, index=False)
    log.info("CSV -> %s", out_csv)

    # ---- summary ----
    n = len(rob)
    counts = {}
    for name in POTS:
        col = f"P_unb_{name}"
        counts[name] = {
            ">0.5": int((rob[col] > 0.5).sum()),
            ">0.7": int((rob[col] > 0.7).sum()),
            ">0.9": int((rob[col] > 0.9).sum()),
        }

    md = []
    md.append("# Galactic-potential robustness check (Step 6D)\n")
    md.append("Counts of unbound candidates from the same 356-star "
              "final-strict sample, recomputed under three independently "
              "published Milky-Way potentials. Distances are Bailer-Jones "
              "geometric, RVs are Gaia DR3, MC = 500 draws/star.\n")
    md.append("| threshold | MWPotential2014 (Bovy 2015) | McMillan17 | Irrgang13I |")
    md.append("|---|---:|---:|---:|")
    for t in (">0.5", ">0.7", ">0.9"):
        md.append(f"| $P_{{\\rm unbound}} {t}$ | "
                  f"{counts['MWPotential2014'][t]} | "
                  f"{counts['McMillan17'][t]} | "
                  f"{counts['Irrgang13I'][t]} |")
    md.append("")

    # how many of MWPot 2014 unbound also unbound in others
    rob["P_max"] = rob[[f"P_unb_{n}" for n in POTS]].max(axis=1)
    rob["P_min"] = rob[[f"P_unb_{n}" for n in POTS]].min(axis=1)
    n_robust05 = int((rob["P_min"] > 0.5).sum())
    n_robust09 = int((rob["P_min"] > 0.9).sum())
    md.append("## Robust unbound across all three potentials\n")
    md.append(f"- Stars with $P_{{\\rm unbound}}>0.5$ in **all three** potentials: **{n_robust05}**")
    md.append(f"- Stars with $P_{{\\rm unbound}}>0.9$ in **all three** potentials: **{n_robust09}**\n")
    md.append("This is the most conservative answer to the referee's "
              "question; only stars that survive every potential variation "
              "tested can be regarded as robust unbound candidates.\n")

    md.append("## Per-star spread on the Top-3 candidates\n")
    md.append("| Gaia DR3 source_id | MWPot2014 | McMillan17 | Irrgang13I | spread |")
    md.append("|---|---:|---:|---:|---:|")
    top3 = rob.sort_values("P_unb_MWPotential2014", ascending=False).head(3)
    for _, r in top3.iterrows():
        spread = float(r["P_max"] - r["P_min"])
        md.append(f"| {r['source_id']} | "
                  f"{r['P_unb_MWPotential2014']:.3f} | "
                  f"{r['P_unb_McMillan17']:.3f} | "
                  f"{r['P_unb_Irrgang13I']:.3f} | "
                  f"{spread:.3f} |")
    md.append("")

    md.append("## Output\n")
    md.append(f"- `{out_csv.relative_to(ROOT)}`")

    out_md = REPORTS_DIR / "potential_robustness.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)

    print()
    print(f"Sample: N={n}")
    for t in (">0.5", ">0.7", ">0.9"):
        line = f"  P_unb {t}: "
        for name in POTS:
            line += f"{name}={counts[name][t]}  "
        print(line)
    print(f"  Robust unbound (>0.5 in all three potentials): {n_robust05}")
    print(f"  Robust unbound (>0.9 in all three potentials): {n_robust09}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
