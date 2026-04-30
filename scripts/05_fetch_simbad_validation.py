"""Step 5: rank candidates by total velocity and validate the top-N via SIMBAD."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.paths import ensure_dirs, INTERIM_DIR, TOP_CANDIDATES_CSV
from caosp_hivel.simbad import validate_top
from caosp_hivel.log import get_logger


def main() -> int:
    ensure_dirs()
    log = get_logger("caosp.step5")

    src = INTERIM_DIR / "hivel_gaia_lamost.parquet"
    if not src.exists():
        log.error("missing %s — run step 4 first", src)
        return 1
    df = pd.read_parquet(src)

    # Heuristic ranking: |radial velocity| from Gaia or LAMOST, plus proper motion magnitude.
    rv_col = "radial_velocity" if "radial_velocity" in df.columns else "rv"
    pm_total = np.hypot(df.get("pmra", 0), df.get("pmdec", 0))
    score = np.abs(df.get(rv_col, 0).fillna(0)) + pm_total
    df = df.assign(_score=score).sort_values("_score", ascending=False)

    cand_cols = [c for c in ("source_id", "ra_gaia", "dec_gaia", "ra", "dec",
                              rv_col, "pmra", "pmdec", "_score") if c in df.columns]
    candidates = df[cand_cols].head(500).copy()
    if "ra_gaia" in candidates.columns:
        candidates = candidates.rename(columns={"ra_gaia": "ra", "dec_gaia": "dec"})

    candidates.to_csv(TOP_CANDIDATES_CSV, index=False)
    log.info("candidates -> %s", TOP_CANDIDATES_CSV)

    validate_top(candidates, ra_col="ra", dec_col="dec")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
