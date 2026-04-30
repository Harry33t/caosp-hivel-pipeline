"""Step 3: load the user-supplied LAMOST catalog file from data/external/lamost/.

We do not auto-download the LAMOST catalog because the official release pages
are interactive and the file is large; placing it in data/external/lamost/
keeps the pipeline reproducible without scraping.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.paths import ensure_dirs, EXTERNAL_DIR
from caosp_hivel.lamost import load_catalog
from caosp_hivel.log import get_logger


def main() -> int:
    ensure_dirs()
    log = get_logger("caosp.step3")
    src_dir = EXTERNAL_DIR / "lamost"
    src_dir.mkdir(parents=True, exist_ok=True)

    files = [p for p in src_dir.iterdir() if p.suffix.lower() in {".csv", ".fits", ".fit", ".parquet"}]
    if not files:
        log.error(
            "no LAMOST catalog found in %s. Download LAMOST DR8/DR9 LRS stellar "
            "parameter catalog from the official release page and place it here.",
            src_dir,
        )
        return 1

    for f in files:
        load_catalog(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
