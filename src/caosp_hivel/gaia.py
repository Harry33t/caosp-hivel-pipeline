"""Gaia DR3 field augmentation via async ADQL with chunked uploads."""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
import pandas as pd
from astroquery.gaia import Gaia

from .paths import RAW_GAIA
from .config import settings, query_fields
from .log import get_logger

log = get_logger("caosp.gaia")

GAIA_TAP = "https://gea.esac.esa.int/tap-server/tap"


def _chunks(seq, n: int):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def fetch_by_source_ids(source_ids: Iterable[int], *, label: str) -> Path:
    """Resolve a list of Gaia DR3 source_ids to the configured field set.

    Resumable: each chunk is written to its own parquet; existing files skipped.
    The merged result lives at ``data/raw/gaia/{label}.parquet``.
    """
    out = RAW_GAIA / f"{label}.parquet"
    if out.exists():
        log.info("skip Gaia %s (cached)", label)
        return out

    fields = ", ".join(f"g.{c}" for c in query_fields()["gaia_dr3"])
    chunk_size = int(settings()["gaia"]["upload_chunk_size"])

    parts: list[pd.DataFrame] = []
    for i, ids in enumerate(_chunks(source_ids, chunk_size)):
        chunk_path = RAW_GAIA / f"{label}__chunk{i:04d}.parquet"
        if chunk_path.exists():
            log.info("  chunk %d cached", i)
            parts.append(pd.read_parquet(chunk_path))
            continue
        log.info("  chunk %d: %d ids", i, len(ids))
        # astroquery requires upload_resource to be a path to a VOTable file.
        from astropy.table import Table
        upload_path = chunk_path.with_suffix(".upload.xml")
        Table({"source_id": list(ids)}).write(upload_path, format="votable", overwrite=True)
        try:
            job = Gaia.launch_job_async(
                query=(
                    f"SELECT {fields} "
                    "FROM gaiadr3.gaia_source AS g "
                    "JOIN tap_upload.ids AS u USING (source_id)"
                ),
                upload_resource=str(upload_path),
                upload_table_name="ids",
            )
            df = job.get_results().to_pandas()
        finally:
            upload_path.unlink(missing_ok=True)
        df.to_parquet(chunk_path, index=False)
        parts.append(df)

    merged = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    merged.to_parquet(out, index=False)
    log.info("Gaia %s: %d rows -> %s", label, len(merged), out)
    return out
