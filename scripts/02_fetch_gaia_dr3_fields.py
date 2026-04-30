"""Step 2: union the source_ids from the three VizieR tables, fetch Gaia DR3
fields, persist per catalogue under data/raw/gaia/."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.paths import ensure_dirs, RAW_VIZIER
from caosp_hivel.config import catalogs
from caosp_hivel.gaia import fetch_by_source_ids
from caosp_hivel.log import get_logger


SOURCE_ID_CANDIDATES = ("source_id", "Gaia", "Source", "GaiaDR3", "GaiaEDR3", "DR3Name")


def _extract_source_ids(df: pd.DataFrame) -> list[int]:
    for col in SOURCE_ID_CANDIDATES:
        if col not in df.columns:
            continue
        s = df[col]
        if not pd.api.types.is_numeric_dtype(s):
            # Some VizieR tables store "Gaia DR3 <id>"; pull the longest digit run.
            s = s.astype(str).str.extract(r"(\d{6,})", expand=False)
        ids = pd.to_numeric(s, errors="coerce").dropna().astype("int64")
        return ids.unique().tolist()
    raise KeyError(f"no Gaia source_id column among {SOURCE_ID_CANDIDATES} in {list(df.columns)[:8]}")


def main() -> int:
    ensure_dirs()
    log = get_logger("caosp.step2")
    for entry in catalogs()["vizier"]:
        label = entry["label"]
        src = RAW_VIZIER / f"{label}.parquet"
        if not src.exists():
            log.warning("missing %s — run step 1 first", src)
            continue
        df = pd.read_parquet(src)
        ids = _extract_source_ids(df)
        log.info("%s: %d unique Gaia DR3 ids", label, len(ids))
        fetch_by_source_ids(ids, label=label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
