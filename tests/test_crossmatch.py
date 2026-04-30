from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.crossmatch import match_radec


def test_exact_match_within_radius():
    left = pd.DataFrame({"ra": [10.0, 20.0], "dec": [0.0, 0.0], "id": [1, 2]})
    right = pd.DataFrame({"ra": [10.00001, 30.0], "dec": [0.0, 0.0], "tag": ["A", "B"]})
    out = match_radec(left, right, radius_arcsec=1.0)
    assert len(out) == 1
    assert out.iloc[0]["id"] == 1
    assert out.iloc[0]["tag"] == "A"
    assert out.iloc[0]["sep_arcsec"] < 1.0


def test_no_match_returns_empty():
    left = pd.DataFrame({"ra": [10.0], "dec": [0.0]})
    right = pd.DataFrame({"ra": [50.0], "dec": [0.0]})
    out = match_radec(left, right, radius_arcsec=1.0)
    assert out.empty


def test_empty_input_safe():
    assert match_radec(pd.DataFrame(), pd.DataFrame()).empty
