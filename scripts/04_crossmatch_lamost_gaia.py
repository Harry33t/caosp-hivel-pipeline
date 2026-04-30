"""Step 4: cross-match the union of Gaia-augmented HV catalogs against LAMOST."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.paths import ensure_dirs, RAW_GAIA, RAW_LAMOST, INTERIM_DIR
from caosp_hivel.config import catalogs
from caosp_hivel.crossmatch import match_radec
from caosp_hivel.log import get_logger


def main() -> int:
    ensure_dirs()
    log = get_logger("caosp.step4")

    gaia_parts = []
    for entry in catalogs()["vizier"]:
        p = RAW_GAIA / f"{entry['label']}.parquet"
        if p.exists():
            df = pd.read_parquet(p)
            df["__src_catalog"] = entry["label"]
            gaia_parts.append(df)
    if not gaia_parts:
        log.error("no Gaia parquet found — run step 2 first")
        return 1
    gaia = pd.concat(gaia_parts, ignore_index=True).drop_duplicates("source_id")
    log.info("Gaia union: %d rows", len(gaia))

    lamost_files = list(RAW_LAMOST.glob("*.parquet"))
    if not lamost_files:
        log.error("no LAMOST parquet — run step 3 first")
        return 1
    lamost = pd.concat([pd.read_parquet(f) for f in lamost_files], ignore_index=True)
    log.info("LAMOST: %d rows", len(lamost))

    matched = match_radec(gaia, lamost, suffix=("_gaia", "_lamost"))
    log.info("matched: %d rows within 1 arcsec", len(matched))

    out = INTERIM_DIR / "hivel_gaia_lamost.parquet"
    matched.to_parquet(out, index=False)
    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
