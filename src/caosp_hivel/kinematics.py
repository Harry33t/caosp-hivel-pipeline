"""Galactic kinematics with Monte Carlo error propagation.

Conventions
-----------
- Distance proxy: 1/parallax (mas -> kpc). Bailer-Jones geometric distances
  can replace this in a future Step 4D.
- Solar parameters (Reid & Brunthaler 2020 / Schönrich+ 2010 / GRAVITY 2018):
    R_sun = 8.122 kpc
    z_sun = 0.0208 kpc
    v_sun = (12.9, 245.6, 7.78) km/s   # galactocentric Cartesian
- Galactic potential: galpy MWPotential2014.

Outputs (per star)
------------------
distance_kpc, U, V, W (LSR), V_total, V_GSR, R_gc, z_gc, x/y/z_gc,
v_esc_local, v_total_over_vesc, P_unbound (MC), V_total_mean, V_total_std
"""
from __future__ import annotations
import warnings
from dataclasses import dataclass
import numpy as np
import pandas as pd
import astropy.units as u
from astropy.coordinates import (
    SkyCoord, Galactocentric, ICRS, CartesianDifferential,
)
from galpy.potential import MWPotential2014, vesc as galpy_vesc

# --- solar / Galactic constants ---
R_SUN_KPC = 8.122
Z_SUN_KPC = 0.0208
V_SUN_GAL = np.array([12.9, 245.6, 7.78])  # km/s, galactocentric Cartesian
V0_GALPY = 220.0                           # galpy natural unit at R0
R0_GALPY = 8.0                             # galpy natural unit (kpc)

GALCEN_FRAME = Galactocentric(
    galcen_distance=R_SUN_KPC * u.kpc,
    z_sun=Z_SUN_KPC * u.kpc,
    galcen_v_sun=CartesianDifferential(*V_SUN_GAL * u.km / u.s),
)


@dataclass
class KinResult:
    distance_kpc: float
    U: float          # km/s, LSR
    V: float
    W: float
    V_total: float    # km/s, |v| in LSR frame
    V_GSR: float      # galactocentric speed
    x_gc: float
    y_gc: float
    z_gc: float
    R_gc: float
    v_esc: float
    v_ratio: float    # V_GSR / v_esc


def _vesc_at(R_kpc: float, z_kpc: float) -> float:
    """Escape speed in km/s at galactocentric R under MWPotential2014.

    Uses galpy's planar v_esc (z=0) as in standard HVS literature
    (Williams+ 2017, Boubert+ 2018, Liao+ 2024 etc.). The z dependence is
    weak compared to other uncertainties in the potential. ``z_kpc`` is
    accepted for future off-plane corrections but ignored for now.
    """
    R_gp = max(R_kpc, 1e-3) / R0_GALPY
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        v = galpy_vesc(MWPotential2014, R_gp)
    return float(v) * V0_GALPY


def compute_one(
    ra_deg: float, dec_deg: float, parallax_mas: float,
    pmra_masyr: float, pmdec_masyr: float, rv_kms: float,
) -> KinResult:
    """One-shot kinematics from Gaia astrometry + RV (no errors)."""
    if not np.isfinite(parallax_mas) or parallax_mas <= 0:
        return KinResult(*([np.nan] * 12))
    d_kpc = 1.0 / parallax_mas

    # Build ICRS coord with full 6D info; let astropy do the transform.
    rv_safe = rv_kms if np.isfinite(rv_kms) else 0.0
    icrs = SkyCoord(
        ra=ra_deg * u.deg, dec=dec_deg * u.deg,
        distance=d_kpc * u.kpc,
        pm_ra_cosdec=pmra_masyr * u.mas / u.yr,
        pm_dec=pmdec_masyr * u.mas / u.yr,
        radial_velocity=rv_safe * u.km / u.s,
        frame="icrs",
    )

    # Galactic LSR-like UVW: use astropy 'galactic' frame's velocity components.
    gal = icrs.transform_to("galactic")
    # gal.velocity is in galactic Cartesian; .d_x/.d_y/.d_z are U,V,W (km/s).
    U = gal.velocity.d_x.to(u.km / u.s).value
    V = gal.velocity.d_y.to(u.km / u.s).value
    W = gal.velocity.d_z.to(u.km / u.s).value
    V_total = float(np.sqrt(U * U + V * V + W * W))

    gc = icrs.transform_to(GALCEN_FRAME)
    x_gc = gc.x.to(u.kpc).value
    y_gc = gc.y.to(u.kpc).value
    z_gc = gc.z.to(u.kpc).value
    R_gc = float(np.hypot(x_gc, y_gc))
    vx = gc.v_x.to(u.km / u.s).value
    vy = gc.v_y.to(u.km / u.s).value
    vz = gc.v_z.to(u.km / u.s).value
    V_GSR = float(np.sqrt(vx * vx + vy * vy + vz * vz))

    v_esc = _vesc_at(R_gc, z_gc)
    v_ratio = V_GSR / v_esc if v_esc > 0 else np.nan

    return KinResult(
        distance_kpc=d_kpc, U=U, V=V, W=W,
        V_total=V_total, V_GSR=V_GSR,
        x_gc=x_gc, y_gc=y_gc, z_gc=z_gc, R_gc=R_gc,
        v_esc=v_esc, v_ratio=v_ratio,
    )


def compute_with_distance(
    ra_deg: float, dec_deg: float, distance_pc: float,
    pmra_masyr: float, pmdec_masyr: float, rv_kms: float,
) -> KinResult:
    """Same as compute_one but takes a distance directly (skips 1/parallax)."""
    if not np.isfinite(distance_pc) or distance_pc <= 0:
        return KinResult(*([np.nan] * 12))
    rv_safe = rv_kms if np.isfinite(rv_kms) else 0.0
    icrs = SkyCoord(
        ra=ra_deg * u.deg, dec=dec_deg * u.deg,
        distance=(distance_pc / 1000.0) * u.kpc,
        pm_ra_cosdec=pmra_masyr * u.mas / u.yr,
        pm_dec=pmdec_masyr * u.mas / u.yr,
        radial_velocity=rv_safe * u.km / u.s,
        frame="icrs",
    )
    gal = icrs.transform_to("galactic")
    U = gal.velocity.d_x.to(u.km / u.s).value
    V = gal.velocity.d_y.to(u.km / u.s).value
    W = gal.velocity.d_z.to(u.km / u.s).value
    V_total = float(np.sqrt(U * U + V * V + W * W))
    gc = icrs.transform_to(GALCEN_FRAME)
    x_gc = gc.x.to(u.kpc).value
    y_gc = gc.y.to(u.kpc).value
    z_gc = gc.z.to(u.kpc).value
    R_gc = float(np.hypot(x_gc, y_gc))
    vx = gc.v_x.to(u.km / u.s).value
    vy = gc.v_y.to(u.km / u.s).value
    vz = gc.v_z.to(u.km / u.s).value
    V_GSR = float(np.sqrt(vx * vx + vy * vy + vz * vz))
    v_esc = _vesc_at(R_gc, z_gc)
    return KinResult(
        distance_kpc=distance_pc / 1000.0, U=U, V=V, W=W,
        V_total=V_total, V_GSR=V_GSR,
        x_gc=x_gc, y_gc=y_gc, z_gc=z_gc, R_gc=R_gc,
        v_esc=v_esc, v_ratio=V_GSR / v_esc if v_esc > 0 else np.nan,
    )


def monte_carlo_with_distance(
    ra_deg: float, dec_deg: float,
    distance_pc: float, dist_err_low: float, dist_err_high: float,
    pmra: float, pmra_err: float,
    pmdec: float, pmdec_err: float,
    rv: float, rv_err: float,
    *, n: int = 1000, rng: np.random.Generator | None = None,
) -> dict:
    """MC with a pre-computed distance (e.g. Bailer-Jones r_med_geo).

    Distance is sampled as log-normal: log10(d) ~ N(log10(d_med), sigma_log)
    with sigma_log = (log10(d_hi) - log10(d_lo)) / 2 to handle the typical
    asymmetric 16th/84th percentile reporting of Bailer-Jones distances.
    Falls back to symmetric Gaussian if either err side is zero/missing.
    """
    rng = rng or np.random.default_rng(42)
    has_rv = np.isfinite(rv)
    if not np.isfinite(distance_pc) or distance_pc <= 0:
        return {"n_mc": 0, "V_total_mean": np.nan, "V_total_std": np.nan,
                "V_GSR_mean": np.nan, "V_GSR_std": np.nan,
                "P_v500": np.nan, "P_unbound": np.nan, "has_rv": has_rv}

    if (np.isfinite(dist_err_low) and np.isfinite(dist_err_high)
            and dist_err_low > 0 and dist_err_high > 0):
        d_hi = distance_pc + dist_err_high
        d_lo = max(distance_pc - dist_err_low, 1e-3)
        sigma_log = (np.log10(d_hi) - np.log10(d_lo)) / 2.0
        log_d = rng.normal(np.log10(distance_pc), max(sigma_log, 1e-4), n)
        d_s = np.power(10.0, log_d)
    else:
        # symmetric 10% fallback if no usable error
        d_s = rng.normal(distance_pc, max(distance_pc * 0.1, 1.0), n)
        d_s = np.where(d_s > 0, d_s, np.nan)

    valid = np.isfinite(d_s) & (d_s > 0)
    if not valid.any():
        return {"n_mc": 0, "V_total_mean": np.nan, "V_total_std": np.nan,
                "V_GSR_mean": np.nan, "V_GSR_std": np.nan,
                "P_v500": np.nan, "P_unbound": np.nan, "has_rv": has_rv}
    d_v = d_s[valid]
    pmra_v = rng.normal(pmra, max(pmra_err, 1e-6), n)[valid]
    pmdec_v = rng.normal(pmdec, max(pmdec_err, 1e-6), n)[valid]
    if has_rv:
        rv_v = rng.normal(rv, max(rv_err, 1e-6), n)[valid]
    else:
        rv_v = np.zeros(int(valid.sum()))

    nv = len(d_v)
    icrs = SkyCoord(
        ra=np.full(nv, ra_deg) * u.deg,
        dec=np.full(nv, dec_deg) * u.deg,
        distance=(d_v / 1000.0) * u.kpc,
        pm_ra_cosdec=pmra_v * u.mas / u.yr,
        pm_dec=pmdec_v * u.mas / u.yr,
        radial_velocity=rv_v * u.km / u.s,
        frame="icrs",
    )
    gal = icrs.transform_to("galactic")
    U = gal.velocity.d_x.to(u.km / u.s).value
    V = gal.velocity.d_y.to(u.km / u.s).value
    W = gal.velocity.d_z.to(u.km / u.s).value
    Vt = np.sqrt(U * U + V * V + W * W)
    gc = icrs.transform_to(GALCEN_FRAME)
    vx = gc.v_x.to(u.km / u.s).value
    vy = gc.v_y.to(u.km / u.s).value
    vz = gc.v_z.to(u.km / u.s).value
    VG = np.sqrt(vx * vx + vy * vy + vz * vz)
    R_arr = np.hypot(gc.x.to(u.kpc).value, gc.y.to(u.kpc).value)
    ve = np.array([_vesc_at(r, 0.0) for r in R_arr])
    vratio = VG / np.where(ve > 0, ve, np.nan)
    return {
        "n_mc": int(nv),
        "V_total_mean": float(np.nanmean(Vt)),
        "V_total_std": float(np.nanstd(Vt)),
        "V_GSR_mean": float(np.nanmean(VG)),
        "V_GSR_std": float(np.nanstd(VG)),
        "P_v500": float(np.mean(VG > 500)),
        "P_unbound": float(np.mean(vratio > 1.0)),
        "has_rv": bool(has_rv),
    }


def monte_carlo(
    ra_deg: float, dec_deg: float,
    parallax_mas: float, parallax_err: float,
    pmra: float, pmra_err: float,
    pmdec: float, pmdec_err: float,
    rv: float, rv_err: float,
    *, n: int = 1000, rng: np.random.Generator | None = None,
) -> dict:
    """Vectorised MC: one SkyCoord of length n per star, one transform call.

    Stars with rv = NaN have RV held at 0 (no sampling); P_unbound is then a
    tangential-only lower bound and the caller should treat them via has_rv.
    """
    rng = rng or np.random.default_rng(42)

    plx_s = rng.normal(parallax_mas, max(parallax_err, 1e-6), n)
    valid = plx_s > 0
    if not valid.any():
        return {"n_mc": 0, "V_total_mean": np.nan, "V_total_std": np.nan,
                "V_GSR_mean": np.nan, "V_GSR_std": np.nan,
                "P_v500": np.nan, "P_unbound": np.nan, "has_rv": False}

    plx_v = plx_s[valid]
    pmra_v = rng.normal(pmra, max(pmra_err, 1e-6), n)[valid]
    pmdec_v = rng.normal(pmdec, max(pmdec_err, 1e-6), n)[valid]
    has_rv = np.isfinite(rv)
    if has_rv:
        rv_v = rng.normal(rv, max(rv_err, 1e-6), n)[valid]
    else:
        rv_v = np.zeros(int(valid.sum()))

    d_kpc = 1.0 / plx_v
    nv = len(d_kpc)

    icrs = SkyCoord(
        ra=np.full(nv, ra_deg) * u.deg,
        dec=np.full(nv, dec_deg) * u.deg,
        distance=d_kpc * u.kpc,
        pm_ra_cosdec=pmra_v * u.mas / u.yr,
        pm_dec=pmdec_v * u.mas / u.yr,
        radial_velocity=rv_v * u.km / u.s,
        frame="icrs",
    )
    gal = icrs.transform_to("galactic")
    U = gal.velocity.d_x.to(u.km / u.s).value
    V = gal.velocity.d_y.to(u.km / u.s).value
    W = gal.velocity.d_z.to(u.km / u.s).value
    Vt = np.sqrt(U * U + V * V + W * W)

    gc = icrs.transform_to(GALCEN_FRAME)
    vx = gc.v_x.to(u.km / u.s).value
    vy = gc.v_y.to(u.km / u.s).value
    vz = gc.v_z.to(u.km / u.s).value
    VG = np.sqrt(vx * vx + vy * vy + vz * vz)
    R_arr = np.hypot(gc.x.to(u.kpc).value, gc.y.to(u.kpc).value)
    # vesc per sample (planar, at the sample's R)
    ve = np.array([_vesc_at(r, 0.0) for r in R_arr])
    vratio = VG / np.where(ve > 0, ve, np.nan)

    return {
        "n_mc": int(nv),
        "V_total_mean": float(np.nanmean(Vt)),
        "V_total_std": float(np.nanstd(Vt)),
        "V_GSR_mean": float(np.nanmean(VG)),
        "V_GSR_std": float(np.nanstd(VG)),
        "P_v500": float(np.mean(VG > 500)),
        "P_unbound": float(np.mean(vratio > 1.0)),
        "has_rv": bool(has_rv),
    }
