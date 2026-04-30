"""Shared HTTP plumbing: rate limiting, exponential backoff, resumable downloads.

All outbound requests should go through this module so the compliance rules
(<=1 rps, polite UA, retry-with-backoff) apply uniformly.
"""
from __future__ import annotations
import time
import threading
from pathlib import Path
from typing import Optional

import requests
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception_type,
    before_sleep_log,
)

from .config import settings
from .log import get_logger

log = get_logger("caosp.net")
_LOCK = threading.Lock()
_LAST_CALL: dict[str, float] = {}


def _throttle(host: str) -> None:
    """Sleep so consecutive calls to the same host respect rate_limit_rps."""
    rps = float(settings()["network"]["rate_limit_rps"])
    min_gap = 1.0 / rps if rps > 0 else 0.0
    with _LOCK:
        now = time.monotonic()
        last = _LAST_CALL.get(host, 0.0)
        wait = (last + min_gap) - now
        if wait > 0:
            time.sleep(wait)
        _LAST_CALL[host] = time.monotonic()


def _session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = settings()["network"]["user_agent"]
    return s


def _retry_decorator():
    r = settings()["network"]["retry"]
    return retry(
        stop=stop_after_attempt(int(r["max_attempts"])),
        wait=wait_exponential(
            multiplier=float(r["backoff_initial_s"]),
            max=float(r["backoff_max_s"]),
            exp_base=float(r["backoff_multiplier"]),
        ),
        retry=retry_if_exception_type((requests.RequestException,)),
        before_sleep=before_sleep_log(log, 30),  # WARNING
        reraise=True,
    )


def get(url: str, **kwargs) -> requests.Response:
    """Throttled+retried HTTP GET. Returns the Response (caller decides what to do)."""
    host = requests.utils.urlparse(url).hostname or "unknown"
    timeout = settings()["network"]["request_timeout_s"]

    @_retry_decorator()
    def _do() -> requests.Response:
        _throttle(host)
        log.debug("GET %s", url)
        with _session() as s:
            r = s.get(url, timeout=timeout, **kwargs)
        r.raise_for_status()
        return r

    return _do()


def download(url: str, dest: Path, *, overwrite: bool = False) -> Path:
    """Resumable file download.

    Writes to ``dest.partial`` first, renames to ``dest`` on success. If
    ``dest`` already exists and ``overwrite`` is False, returns immediately —
    that is the resume primitive.
    """
    dest = Path(dest)
    if dest.exists() and not overwrite:
        log.info("skip (already on disk): %s", dest)
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    host = requests.utils.urlparse(url).hostname or "unknown"
    timeout = settings()["network"]["request_timeout_s"]

    @_retry_decorator()
    def _do() -> None:
        _throttle(host)
        log.info("download %s -> %s", url, dest)
        with _session() as s, s.get(url, timeout=timeout, stream=True) as r:
            r.raise_for_status()
            with tmp.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    if chunk:
                        fh.write(chunk)
        tmp.replace(dest)

    _do()
    return dest
