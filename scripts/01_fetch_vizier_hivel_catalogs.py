"""Step 1: download three high-velocity-star catalogues from VizieR."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.paths import ensure_dirs
from caosp_hivel.vizier import fetch_all
from caosp_hivel.log import get_logger


def main() -> int:
    ensure_dirs()
    log = get_logger("caosp.step1")
    paths = fetch_all()
    for p in paths:
        log.info("ready: %s", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
