"""Load YAML config files into plain dicts. Single source of truth for tunables."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import os
import yaml

from .paths import CONFIG_DIR


def _load_yaml(name: str) -> dict:
    path: Path = CONFIG_DIR / name
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def settings() -> dict:
    cfg = _load_yaml("settings.yaml")
    # Allow env-var overrides for the most-tweaked knobs.
    if (rps := os.environ.get("CAOSP_RATE_LIMIT_RPS")):
        cfg.setdefault("network", {})["rate_limit_rps"] = float(rps)
    if (ua := os.environ.get("CAOSP_USER_AGENT")):
        cfg.setdefault("network", {})["user_agent"] = ua
    return cfg


@lru_cache(maxsize=1)
def catalogs() -> dict:
    return _load_yaml("catalogs.yaml")


@lru_cache(maxsize=1)
def query_fields() -> dict:
    return _load_yaml("query_fields.yaml")
