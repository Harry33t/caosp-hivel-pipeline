"""Step 6: produce the master CSV consumed by the paper repo."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.paths import ensure_dirs, INTERIM_DIR, MASTER_CSV, RAW_SIMBAD
from caosp_hivel.log import get_logger


def main() -> int:
    ensure_dirs()
    log = get_logger("caosp.step6")

    src = INTERIM_DIR / "hivel_gaia_lamost.parquet"
    if not src.exists():
        log.error("missing %s", src)
        return 1
    df = pd.read_parquet(src)

    simbad_csv = RAW_SIMBAD / "top_candidates_simbad.csv"
    if simbad_csv.exists():
        sim = pd.read_csv(simbad_csv)
        # Coarse 6-decimal RA/Dec join — same key SIMBAD step writes.
        for col in ("ra", "dec"):
            if col in df.columns:
                df[f"_{col}_k"] = df[col].round(6)
        sim["_ra_k"], sim["_dec_k"] = sim["ra"].round(6), sim["dec"].round(6)
        df = df.merge(sim[["_ra_k", "_dec_k", "main_id", "otype"]],
                      on=["_ra_k", "_dec_k"], how="left")
        df = df.drop(columns=[c for c in df.columns if c.startswith("_") and c.endswith("_k")])

    df.to_csv(MASTER_CSV, index=False)
    log.info("master -> %s (%d rows)", MASTER_CSV, len(df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
