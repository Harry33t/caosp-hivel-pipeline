"""Lightweight IO helpers."""
from __future__ import annotations
from pathlib import Path
import pandas as pd


def write_parquet(df: pd.DataFrame, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def write_csv(df: pd.DataFrame, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def read_table(path: Path) -> pd.DataFrame:
    path = Path(path)
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)
    if suf in {".csv", ".tsv"}:
        return pd.read_csv(path, sep="," if suf == ".csv" else "\t")
    if suf in {".fits", ".fit"}:
        from astropy.table import Table
        return Table.read(path).to_pandas()
    raise ValueError(f"unsupported extension: {suf}")
