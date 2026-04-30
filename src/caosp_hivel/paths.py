"""Centralized filesystem paths. Scripts must import from here, never hard-code."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"

RAW_VIZIER = RAW_DIR / "vizier"
RAW_GAIA = RAW_DIR / "gaia"
RAW_LAMOST = RAW_DIR / "lamost"
RAW_SIMBAD = RAW_DIR / "simbad"

CACHE_DIR = ROOT / "cache"
LOGS_DIR = ROOT / "logs"

MASTER_CSV = PROCESSED_DIR / "hivel_gaia_lamost_master.csv"
TOP_CANDIDATES_CSV = PROCESSED_DIR / "top_candidates_for_simbad.csv"


def ensure_dirs() -> None:
    for p in (
        RAW_VIZIER, RAW_GAIA, RAW_LAMOST, RAW_SIMBAD,
        INTERIM_DIR, PROCESSED_DIR, EXTERNAL_DIR,
        CACHE_DIR, LOGS_DIR,
    ):
        p.mkdir(parents=True, exist_ok=True)
