"""VizieR fetchers — three high-velocity-star catalogues."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from astroquery.vizier import Vizier

from .paths import RAW_VIZIER
from .config import catalogs
from .log import get_logger

log = get_logger("caosp.vizier")


def fetch_one(catalog_id: str, label: str, table: str | None = None) -> Path:
    """Download every sub-table of a VizieR record. Returns the canonical
    parquet path. ``table`` (e.g. ``J/AJ/166/12/table5``) picks which sub-table
    is canonical — required when ``table[0]`` is not the desired one.
    Resumable via ``exists()`` check."""
    out = RAW_VIZIER / f"{label}.parquet"
    if out.exists():
        log.info("skip %s (cached at %s)", catalog_id, out)
        return out

    log.info("VizieR get_catalogs(%s)", catalog_id)
    v = Vizier(row_limit=-1)
    table_list = v.get_catalogs(catalog_id)
    if len(table_list) == 0:
        raise RuntimeError(f"no tables returned for {catalog_id}")

    chosen_idx = 0
    for i, tbl in enumerate(table_list):
        df = tbl.to_pandas()
        sub = RAW_VIZIER / f"{label}__t{i}.parquet"
        df.to_parquet(sub, index=False)
        name = tbl.meta.get("name", "")
        log.info("  table[%d] %s: %d rows -> %s", i, name, len(df), sub)
        if table and name == table:
            chosen_idx = i

    if table and table_list[chosen_idx].meta.get("name") != table:
        raise RuntimeError(f"requested table '{table}' not found in {catalog_id}")

    log.info("  canonical -> table[%d] (%s)", chosen_idx,
             table_list[chosen_idx].meta.get("name", "?"))
    table_list[chosen_idx].to_pandas().to_parquet(out, index=False)
    return out


def fetch_all() -> list[Path]:
    paths = []
    for entry in catalogs()["vizier"]:
        paths.append(fetch_one(entry["id"], entry["label"], entry.get("table")))
    return paths
