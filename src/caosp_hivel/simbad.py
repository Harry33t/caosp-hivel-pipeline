"""SIMBAD validation — small batches only, never high-frequency."""
from __future__ import annotations
import time
from pathlib import Path
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.simbad import Simbad

from .paths import RAW_SIMBAD
from .config import settings
from .log import get_logger

log = get_logger("caosp.simbad")


def _customized() -> Simbad:
    s = Simbad()
    s.ROW_LIMIT = 1
    s.TIMEOUT = settings()["network"]["request_timeout_s"]
    for f in settings()["simbad"]["fields"]:
        try:
            s.add_votable_fields(f)
        except Exception as e:
            log.warning("SIMBAD field unavailable: %s (%s)", f, e)
    return s


def validate_top(candidates: pd.DataFrame, *, ra_col: str = "ra", dec_col: str = "dec",
                 radius_arcsec: float = 2.0) -> Path:
    """Query SIMBAD one-by-one for the top-N candidates. Throttled by net rate
    limit. Result is appended row-by-row so a crash mid-loop is recoverable."""
    out = RAW_SIMBAD / "top_candidates_simbad.csv"
    n = int(settings()["simbad"]["top_n"])
    df = candidates.head(n).reset_index(drop=True)

    rps = float(settings()["network"]["rate_limit_rps"])
    min_gap = 1.0 / rps if rps > 0 else 0.0
    s = _customized()

    written = set()
    if out.exists():
        prev = pd.read_csv(out)
        written = set(zip(prev[ra_col].round(6), prev[dec_col].round(6)))
        log.info("resuming SIMBAD with %d rows already done", len(written))
        prev.to_csv(out, index=False)
    else:
        out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for _, row in df.iterrows():
        key = (round(row[ra_col], 6), round(row[dec_col], 6))
        if key in written:
            continue
        coord = SkyCoord(row[ra_col] * u.deg, row[dec_col] * u.deg, frame="icrs")
        try:
            res = s.query_region(coord, radius=radius_arcsec * u.arcsec)
        except Exception as e:
            log.warning("SIMBAD error at (%.5f, %.5f): %s", row[ra_col], row[dec_col], e)
            res = None
        rec = {ra_col: row[ra_col], dec_col: row[dec_col]}
        if res is not None and len(res) > 0:
            rec["main_id"] = str(res[0]["MAIN_ID"])
            rec["otype"] = str(res[0].get("OTYPE", ""))
        rows.append(rec)
        # incremental write — partial progress survives interruption
        pd.DataFrame(rows).to_csv(out, index=False, mode="w")
        time.sleep(min_gap)

    log.info("SIMBAD validation -> %s", out)
    return out
