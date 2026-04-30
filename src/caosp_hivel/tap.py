"""Generic async TAP/ADQL helper with persisted job IDs (resume primitive)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import pyvo

from .paths import CACHE_DIR
from .log import get_logger

log = get_logger("caosp.tap")
_JOBS_FILE = CACHE_DIR / "tap_jobs.json"


def _load_jobs() -> dict:
    if _JOBS_FILE.exists():
        return json.loads(_JOBS_FILE.read_text(encoding="utf-8"))
    return {}


def _save_jobs(d: dict) -> None:
    _JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _JOBS_FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")


def submit_async(service_url: str, adql: str, *, key: str) -> pyvo.dal.AsyncTAPJob:
    """Submit (or resume) a TAP async job. ``key`` identifies the logical query
    so subsequent runs can recover the same job URL."""
    jobs = _load_jobs()
    if key in jobs:
        try:
            job = pyvo.dal.AsyncTAPJob(jobs[key])
            log.info("resumed TAP job %s (%s)", key, jobs[key])
            return job
        except Exception as e:  # job expired server-side
            log.warning("stale job for %s (%s); resubmitting", key, e)

    service = pyvo.dal.TAPService(service_url)
    job = service.submit_job(adql)
    job.run()
    jobs[key] = job.url
    _save_jobs(jobs)
    log.info("submitted TAP job %s -> %s", key, job.url)
    return job


def fetch_async(service_url: str, adql: str, *, key: str):
    """Submit-or-resume, wait for completion, return an astropy Table."""
    job = submit_async(service_url, adql, key=key)
    job.wait()
    job.raise_if_error()
    return job.fetch_result().to_table()
