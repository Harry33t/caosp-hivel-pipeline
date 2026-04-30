from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caosp_hivel.config import settings, catalogs, query_fields


def test_settings_has_rate_limit():
    assert settings()["network"]["rate_limit_rps"] > 0


def test_three_vizier_catalogs():
    ids = [c["id"] for c in catalogs()["vizier"]]
    assert ids == ["J/ApJS/252/3", "J/AJ/166/12", "J/AJ/167/76"]


def test_gaia_fields_complete():
    fields = query_fields()["gaia_dr3"]
    must_have = {"source_id", "parallax", "ruwe", "radial_velocity"}
    assert must_have.issubset(set(fields))
