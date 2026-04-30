"""Optional unified entry: ``python -m caosp_hivel.cli <step>``."""
from __future__ import annotations
import argparse
import sys

STEPS = ["env", "vizier", "gaia", "lamost", "xmatch", "simbad", "final"]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="caosp_hivel")
    p.add_argument("step", choices=STEPS)
    args = p.parse_args(argv)

    if args.step == "env":
        from scripts import _bootstrap  # noqa: F401  # if used as package
    # Delegate to scripts/ to keep a single source of truth for orchestration.
    import runpy
    mapping = {
        "env": "scripts/00_check_env.py",
        "vizier": "scripts/01_fetch_vizier_hivel_catalogs.py",
        "gaia": "scripts/02_fetch_gaia_dr3_fields.py",
        "lamost": "scripts/03_fetch_lamost_catalogs.py",
        "xmatch": "scripts/04_crossmatch_lamost_gaia.py",
        "simbad": "scripts/05_fetch_simbad_validation.py",
        "final": "scripts/06_build_final_dataset.py",
    }
    runpy.run_path(mapping[args.step], run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
