"""Smoke-test imports, write permissions, and config loading."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.paths import ensure_dirs, ROOT
from caosp_hivel.config import settings, catalogs, query_fields
from caosp_hivel.log import get_logger


def main() -> int:
    log = get_logger("caosp.env")
    ensure_dirs()
    log.info("project root: %s", ROOT)
    log.info("rate limit: %s rps", settings()["network"]["rate_limit_rps"])
    log.info("vizier catalogs: %s", [c["id"] for c in catalogs()["vizier"]])
    log.info("gaia fields: %d", len(query_fields()["gaia_dr3"]))
    log.info("env OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
