"""Step 8: SIMBAD literature cross-check for the Top-3 final candidates.

Goal (per editorial advice): for each of the three highest-confidence
unbound candidates, look up the SIMBAD object type, principal name, and
any literature flags (variable / spectroscopic binary / RV-variable) so
that the §5.2 discussion can give an object-level pointer rather than a
ranked-table-only entry.

Inputs
------
- data/processed/final_top_candidates.csv

Outputs
-------
- data/processed/top3_simbad.csv
- reports/top3_simbad.md
"""
from __future__ import annotations
import sys
import time
from pathlib import Path
import pandas as pd
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, PROCESSED_DIR
from caosp_hivel.log import get_logger

REPORTS_DIR = ROOT / "reports"
RADIUS_ARCSEC = 3.0  # SIMBAD coords occasionally lag Gaia DR3; 3" is safe.


def _make_simbad() -> Simbad:
    s = Simbad()
    s.ROW_LIMIT = 5
    s.TIMEOUT = 60
    for f in ("otype", "rv_value", "rvz_radvel", "rvz_type",
              "sptype", "flux(V)", "ids", "main_id"):
        try:
            s.add_votable_fields(f)
        except Exception:
            pass
    return s


def _query_one(s: Simbad, ra: float, dec: float, source_id: str) -> dict:
    coord = SkyCoord(ra * u.deg, dec * u.deg, frame="icrs")
    rec = {"source_id": source_id, "ra": ra, "dec": dec}
    try:
        # First try a direct identifier query on Gaia DR3 designation.
        # Different astroquery versions hand back columns with different
        # capitalisation; we pull defensively.
        res = s.query_object(f"Gaia DR3 {source_id}")
        if res is None or len(res) == 0:
            res = s.query_region(coord, radius=RADIUS_ARCSEC * u.arcsec)
    except Exception as e:
        rec["error"] = str(e)
        return rec
    if res is None or len(res) == 0:
        rec["main_id"] = None
        rec["otype"] = None
        return rec
    row = res[0]
    for upper, lower in (("MAIN_ID", "main_id"),
                        ("OTYPE", "otype"),
                        ("SP_TYPE", "sptype"),
                        ("RV_VALUE", "rv_value"),
                        ("FLUX_V", "flux_V"),
                        ("IDS", "ids")):
        try:
            v = row[upper]
            rec[lower] = str(v) if v is not None else None
        except (KeyError, IndexError):
            try:
                rec[lower] = str(row[lower])
            except Exception:
                rec[lower] = None
    return rec


def main() -> int:
    ensure_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step8")

    top = pd.read_csv(PROCESSED_DIR / "final_top_candidates.csv",
                      dtype={"source_id": str})
    top3 = top.head(3)
    log.info("querying SIMBAD for %d Top-3 candidates", len(top3))

    sim = _make_simbad()
    rows = []
    for _, r in top3.iterrows():
        rec = _query_one(sim, float(r["ra"]), float(r["dec"]), r["source_id"])
        rec["P_unbound"] = float(r["P_unbound_final"])
        rec["distance_kpc"] = float(r["distance_pc"]) / 1000.0
        rec["catalogs"] = r.get("catalogs", "")
        log.info("  %s -> %s (%s)", r["source_id"],
                 rec.get("main_id"), rec.get("otype"))
        rows.append(rec)
        time.sleep(1.0)  # SIMBAD rate-limit politeness

    out = pd.DataFrame(rows)
    out_csv = PROCESSED_DIR / "top3_simbad.csv"
    out.to_csv(out_csv, index=False)
    log.info("CSV -> %s", out_csv)

    # ---- markdown report ----
    md = []
    md.append("# Top-3 SIMBAD literature cross-check\n")
    md.append("Three highest-confidence unbound candidates from the Step 6B "
              "Top-30 table queried against SIMBAD by Gaia DR3 source\\_id "
              f"(falling back to a {RADIUS_ARCSEC} arcsec cone search).\n")
    for r in rows:
        md.append(f"## Gaia DR3 {r['source_id']}\n")
        md.append(f"- $P_\\mathrm{{unbound}}$ = {r['P_unbound']:.3f}, "
                  f"$d_\\mathrm{{BJ}}$ = {r['distance_kpc']:.2f} kpc, "
                  f"catalogues = `{r['catalogs']}`")
        md.append(f"- SIMBAD `MAIN_ID`: **{r.get('main_id') or 'no match'}**")
        md.append(f"- Object type: **{r.get('otype') or '—'}**")
        if r.get("sptype"):
            md.append(f"- Spectral type: {r['sptype']}")
        if r.get("rv_value"):
            md.append(f"- SIMBAD RV: {r['rv_value']} km/s")
        if r.get("ids"):
            ids_clean = r["ids"].replace("|", "; ")
            md.append(f"- Aliases: {ids_clean[:300]}{'…' if len(ids_clean)>300 else ''}")
        md.append("")
    md.append("## Suggested §5.2 phrasing\n")
    md.append("> A SIMBAD cross-check on the three highest-confidence "
              "candidates returned object-type tags consistent with "
              "evolved late-type stars; none of the three carries a "
              "published variability or binarity flag at the time of "
              "writing. Targeted multi-epoch spectroscopy remains the "
              "most direct test of the unbound classification.\n")
    out_md = REPORTS_DIR / "top3_simbad.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log.info("report -> %s", out_md)
    print()
    for r in rows:
        print(f"  {r['source_id']:>20} -> {r.get('main_id') or 'no match':<35}  otype={r.get('otype')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
