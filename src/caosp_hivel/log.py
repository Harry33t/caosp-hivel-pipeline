"""Project logger. Named log.py (not logging.py) to avoid stdlib shadowing."""
from __future__ import annotations
import logging
import logging.handlers
from pathlib import Path

from .paths import LOGS_DIR
from .config import settings

_INITIALIZED = False


def get_logger(name: str = "caosp") -> logging.Logger:
    global _INITIALIZED
    logger = logging.getLogger(name)
    if _INITIALIZED:
        return logger

    cfg = settings().get("logging", {})
    level = getattr(logging, cfg.get("level", "INFO").upper(), logging.INFO)
    log_file = Path(cfg.get("file", "logs/download.log"))
    if not log_file.is_absolute():
        log_file = LOGS_DIR.parent / log_file
    log_file.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setFormatter(fmt)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)

    root = logging.getLogger("caosp")
    root.setLevel(level)
    root.addHandler(fh)
    root.addHandler(sh)
    root.propagate = False

    _INITIALIZED = True
    return logger
