"""Regression test guarding 19-digit Gaia DR3 source_id integrity.

A 19-digit Gaia DR3 source_id (~1e18) overflows the 53-bit mantissa of a
Python ``float``. Any code path that routes such an integer through
``float64`` — including ``"{:.0f}".format(int_value)`` and pandas Stylers —
silently truncates the trailing 3-4 digits.

This test asserts that, for the published Top-30 candidate table, the
source_ids in:

    data/processed/final_top_candidates.csv
    paper/tables/table3_final_top_candidates.csv
    paper/tables/table3_final_top_candidates.tex

are byte-identical to each other and round-trip cleanly through ``int()``.
Two known-good source_ids are pinned as anchor cases.
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]

CSV_FINAL_TOP = ROOT / "data" / "processed" / "final_top_candidates.csv"
CSV_TABLE3    = ROOT / "paper" / "tables" / "table3_final_top_candidates.csv"
TEX_TABLE3    = ROOT / "paper" / "tables" / "table3_final_top_candidates.tex"

# Anchor Top-1 / Top-2 source_ids that demonstrated the original bug
# (their last few digits used to flip when routed through float64).
ANCHOR_SOURCE_IDS = ["1383279090527227264", "1204061267883975040"]


def _ids_from_final_top_csv() -> list[str]:
    """source_id column of the Step 6B CSV (canonical name 'source_id')."""
    df = pd.read_csv(CSV_FINAL_TOP, dtype={"source_id": str})
    return df["source_id"].astype(str).tolist()


def _ids_from_table3_csv() -> list[str]:
    """First column of the Step 7 CSV. Header is LaTeX-flavoured, so we
    read positionally."""
    df = pd.read_csv(CSV_TABLE3, dtype=str)
    return df.iloc[:, 0].astype(str).tolist()


def _ids_from_table3_tex() -> list[str]:
    """Pull the leading 19-digit token from each data row of the LaTeX
    tabular. We deliberately do NOT use a LaTeX parser; the regex matches
    only the leftmost long-digit run on a line that ends with `\\\\`."""
    text = TEX_TABLE3.read_text(encoding="utf-8")
    ids = []
    for line in text.splitlines():
        if not line.rstrip().endswith(r"\\"):
            continue
        m = re.match(r"\s*(\d{17,20})\b", line)
        if m:
            ids.append(m.group(1))
    return ids


# ---------- file existence ----------
@pytest.mark.parametrize("path", [CSV_FINAL_TOP, CSV_TABLE3, TEX_TABLE3])
def test_files_exist(path: Path) -> None:
    assert path.exists(), f"missing: {path}"


# ---------- inter-file consistency ----------
def test_three_files_agree_on_top30():
    a = _ids_from_final_top_csv()
    b = _ids_from_table3_csv()
    c = _ids_from_table3_tex()

    assert len(a) == 30, f"final_top_candidates.csv has {len(a)} rows, expected 30"
    assert len(b) == 30, f"table3 csv has {len(b)} rows, expected 30"
    assert len(c) == 30, f"table3 tex parsed {len(c)} ids, expected 30"

    # Compare row-wise. Show the first mismatching row to make failures
    # actionable.
    for i, (x, y, z) in enumerate(zip(a, b, c), 1):
        assert x == y == z, (
            f"row {i} disagree: final_top.csv={x} table3.csv={y} table3.tex={z}"
        )


# ---------- format hygiene ----------
@pytest.mark.parametrize("ids_fn", [
    _ids_from_final_top_csv, _ids_from_table3_csv, _ids_from_table3_tex,
])
def test_no_scientific_or_decimal(ids_fn) -> None:
    for sid in ids_fn():
        assert "e" not in sid.lower(), f"scientific notation in source_id: {sid!r}"
        assert "." not in sid, f"decimal point in source_id: {sid!r}"
        assert sid.isdigit(), f"non-digit chars in source_id: {sid!r}"


@pytest.mark.parametrize("ids_fn", [
    _ids_from_final_top_csv, _ids_from_table3_csv, _ids_from_table3_tex,
])
def test_lengths_and_round_trip_int(ids_fn) -> None:
    for sid in ids_fn():
        # Gaia DR3 source_ids are between ~10^9 and ~10^19; in our master
        # sample they are all 18 or 19 digits long.
        assert 17 <= len(sid) <= 20, f"unexpected length for source_id: {sid!r}"
        # Round-trip: str → int → str must be the same string.
        assert str(int(sid)) == sid, f"int round-trip changed source_id: {sid!r}"


# ---------- pinned anchor IDs ----------
def test_anchor_ids_present_unmodified():
    csv_a = _ids_from_final_top_csv()
    csv_b = _ids_from_table3_csv()
    tex_c = _ids_from_table3_tex()
    for anchor in ANCHOR_SOURCE_IDS:
        assert anchor in csv_a, (
            f"anchor {anchor} missing from final_top_candidates.csv "
            f"(neighbouring ids: {csv_a[:3]})"
        )
        assert anchor in csv_b, f"anchor {anchor} missing from table3 csv"
        assert anchor in tex_c, f"anchor {anchor} missing from table3 tex"


def test_anchor_float_corruption_demonstrated():
    """Sanity: confirm that the original bug WOULD actually corrupt these
    ids if reintroduced. If this assertion ever fails, it likely means a
    future float64 of larger precision is in use (good news), or the
    anchor ids drifted (in which case the test list should be updated).
    """
    for anchor in ANCHOR_SOURCE_IDS:
        true_int = int(anchor)
        broken = int(float(true_int))
        assert broken != true_int, (
            f"anchor {anchor} unexpectedly survives float64 round-trip; "
            "pick a different anchor to keep this test meaningful."
        )
