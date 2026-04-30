"""LAMOST DR9 LRS catalog loader.

We do NOT download spectra. Catalogs (gzipped CSVs) live in
``data/external/lamost/`` and are read with the columns we actually need.
LAMOST uses ``-999`` (and similar magic numbers) as a missing-value sentinel
which we convert to NaN.

Two release files are supported:
- *_LRS_stellar.csv.gz   : 47 cols, includes rv/teff/logg/feh/alpha
- *_LRS_catalogue.csv.gz : 36 cols, basic obs/photometry only (no stellar params)
"""
from __future__ import annotations
import gzip
from pathlib import Path
from typing import Iterable, Optional
import numpy as np
import pandas as pd

from .paths import EXTERNAL_DIR
from .log import get_logger

log = get_logger("caosp.lamost")

# values LAMOST uses for "missing"
LAMOST_NAN_SENTINELS = (-999.0, -9999.0)

# canonical column groups we care about, with possible upstream aliases
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "obsid":          ("obsid", "specid"),
    "designation":    ("designation",),
    "gaia_source_id": ("gaia_source_id", "Gaia DR3 source_id"),
    "ra":             ("ra",),
    "dec":            ("dec",),
    "ra_obs":         ("ra_obs",),
    "dec_obs":        ("dec_obs",),
    "snru":           ("snru",),
    "snrg":           ("snrg",),
    "snrr":           ("snrr",),
    "snri":           ("snri",),
    "snrz":           ("snrz",),
    "class":          ("class",),
    "subclass":       ("subclass",),
    "teff":           ("teff",),
    "teff_err":       ("teff_err",),
    "logg":           ("logg",),
    "logg_err":       ("logg_err",),
    "feh":            ("feh", "[Fe/H]"),
    "feh_err":        ("feh_err",),
    "rv":             ("rv", "radial_velocity"),
    "rv_err":         ("rv_err", "radial_velocity_err"),
    "alpha_m":        ("alpha_m",),
    "alpha_m_err":    ("alpha_m_err",),
}


def discover_files(directory: Path | str | None = None) -> list[Path]:
    """Return any LAMOST catalog files found in directory."""
    d = Path(directory) if directory else (EXTERNAL_DIR / "lamost")
    if not d.is_dir():
        return []
    return sorted(
        p for p in d.iterdir()
        if p.is_file() and p.suffix.lower() in (".gz", ".csv", ".fits", ".fit", ".parquet")
    )


def read_header(path: Path) -> list[str]:
    """Cheaply read just the CSV header (handles .gz transparently)."""
    opener = gzip.open if path.suffix.lower() == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        return f.readline().strip().split(",")


def schema(path: Path) -> dict:
    """Lightweight schema info: file, size, header, recognised canonical fields."""
    header = read_header(path)
    canonical = {}
    for canon, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a in header:
                canonical[canon] = a
                break
    return {
        "path": path,
        "size_mb": path.stat().st_size / 1e6,
        "n_columns": len(header),
        "header": header,
        "canonical": canonical,
    }


def _normalize(df: pd.DataFrame, schema_canonical: dict[str, str]) -> pd.DataFrame:
    """Rename to canonical names, replace -999 sentinels with NaN."""
    rename = {raw: canon for canon, raw in schema_canonical.items() if raw != canon}
    df = df.rename(columns=rename)
    num_cols = df.select_dtypes(include="number").columns
    for s in LAMOST_NAN_SENTINELS:
        df[num_cols] = df[num_cols].mask(df[num_cols] == s, np.nan)
    return df


def load_full(path: Path, *, columns: Optional[Iterable[str]] = None,
              chunksize: int = 500_000) -> pd.DataFrame:
    """Stream-read a LAMOST catalog, keeping only ``columns`` (canonical names).

    ``columns`` is a subset of canonical names from ``COLUMN_ALIASES``;
    canonicals not present in this file are silently skipped.
    """
    info = schema(path)
    canonical = info["canonical"]

    if columns is None:
        wanted = list(canonical.values())
    else:
        wanted = [canonical[c] for c in columns if c in canonical]
    if not wanted:
        raise ValueError(f"none of the requested columns exist in {path}")

    log.info("LAMOST stream %s (%.0f MB), %d cols",
             path.name, info["size_mb"], len(wanted))

    parts: list[pd.DataFrame] = []
    reader = pd.read_csv(
        path, compression="infer", usecols=wanted,
        chunksize=chunksize, low_memory=False,
    )
    total = 0
    for chunk in reader:
        chunk = _normalize(chunk, canonical)
        parts.append(chunk)
        total += len(chunk)
    df = pd.concat(parts, ignore_index=True)
    log.info("LAMOST loaded: %d rows", len(df))
    return df
