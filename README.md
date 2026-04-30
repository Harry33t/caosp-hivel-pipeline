# caosp-hivel-pipeline

A reproducible Gaia DR3 + LAMOST DR9 analysis pipeline for high-velocity
star (HVS) candidate samples drawn from VizieR-published catalogues. The
pipeline pulls public catalogue data, cross-matches it, derives
Galactocentric kinematics with Monte Carlo error propagation, and
isolates the impact of the distance estimator on unbound classification.

## What the pipeline does

1. **Catalogue ingest** — three high-velocity-star candidate catalogues
   from VizieR via `astroquery.vizier`.
2. **Gaia DR3 enrichment** — astrometry, photometry, RV and `ruwe` via
   asynchronous TAP upload-joins against `gaiadr3.gaia_source`.
3. **Bailer-Jones distance attachment** — geometric distances from
   `external.gaiaedr3_distance` (Bailer-Jones et al. 2021), with
   per-source 16th/84th percentiles for log-normal MC sampling.
4. **LAMOST DR9 LRS cross-match** — 1″ sky cross-match against the
   public stellar-parameter catalogue, with multi-epoch handling and a
   best-SNR record selection.
5. **Sample-quality flags** — `q_gaia_astrometry`, `q_lamost_quality`,
   Gaia/LAMOST RV consistency, plus the resulting analysis sub-samples.
6. **Galactocentric kinematics** — $U/V/W$, $v_{\rm grf}$ and the local
   escape speed $v_{\rm esc}(R_{\rm gc})$ under the galpy
   `MWPotential2014` Galactic potential, with 1000-draw Monte Carlo
   uncertainty propagation per star.
7. **Distance-estimator sensitivity** — same-sample re-runs with
   $1/\varpi$ vs Bailer-Jones distances on the final-strict subset.
8. **Radial-velocity sensitivity** — same-sample re-runs with Gaia DR3
   RV vs LAMOST RV on the final-strict subset.

## Compliance & ethics

The HTTP layer (`src/caosp_hivel/net.py`) enforces:

- ≤ 1 request/s per external host (configurable in
  `config/settings.yaml`);
- a polite `User-Agent` carrying a contact address;
- exponential-backoff retries via `tenacity`;
- resumable runs: cached outputs are skipped, TAP async jobs are
  persisted in `cache/tap_jobs.json`;
- no browser emulation, no proxy pools, no CAPTCHA bypass, no
  full-archive scraping. The Gaia full source table and LAMOST spectra
  are never downloaded.

## Layout

```
caosp-hivel-pipeline/
├── config/                YAML knobs (rates, fields, catalogue ids)
├── src/caosp_hivel/       library modules (net, tap, kinematics, ...)
├── scripts/               00–08 numbered pipeline entry points
├── tests/                 pytest, including a 19-digit source_id
│                          integrity guard
├── data/                  staging directories (mostly .gitignored)
└── notebooks/             optional exploratory notebooks
```

## How to run

```bash
# 1) Python 3.10+ environment.
python -m venv .venv && .venv/Scripts/python -m pip install -e .[dev]

# 2) Public Gaia + VizieR fetches. Resumable.
python scripts/00_check_env.py
python scripts/01_fetch_vizier_hivel_catalogs.py
python scripts/02_fetch_gaia_dr3_fields.py
python scripts/04D_bailer_jones_distance.py

# 3) LAMOST DR9 LRS (~2 GB; not redistributed in this repo). Place the
#    public file under data/external/lamost/dr9_v2.0_LRS_stellar.csv.gz.
python scripts/05_lamost_crossmatch.py

# 4) Sample definition + final kinematics.
python scripts/04A_build_gaia_master_qc.py
python scripts/04B_kinematics_mc.py
python scripts/06_define_final_sample.py
python scripts/06B_final_kinematics.py
python scripts/06C_same_sample_distance_sensitivity.py
python scripts/07_paper_figures_tables.py
python scripts/08_top3_simbad_check.py
```

`make all` runs the full chain; `pytest -q` runs the unit tests.

## Software dependencies

`astropy`, `astroquery`, `pyvo`, `galpy`, `pandas`, `numpy`, `scipy`,
`tenacity`, `pyarrow`, `matplotlib`. Pinned in `pyproject.toml` /
`requirements.txt`.

## Citing the upstream archives

If you use this code or its outputs, please acknowledge the Gaia,
LAMOST, VizieR and SIMBAD archives following the templates in
[`CITATION.md`](CITATION.md).

## License

[MIT](LICENSE). Catalogues fetched from VizieR, the Gaia archive and
LAMOST remain governed by their own distribution terms.
