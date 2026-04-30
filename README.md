# caosp-hivel-pipeline

Reproducible Gaia DR3 + LAMOST DR9 reassessment of three published
high-velocity-star catalogues
([Li et al. 2021](https://doi.org/10.3847/1538-4365/abc16e),
[Li et al. 2023](https://doi.org/10.3847/1538-3881/acd1dc),
[Liao et al. 2024](https://doi.org/10.3847/1538-3881/ad18c4))
and the companion code for the manuscript

> *A Gaia DR3–LAMOST reassessment of high-velocity star candidates with
> geometric-distance-aware kinematics*
> F.\ Li and G.\ Huang, submitted to
> *Contributions of the Astronomical Observatory Skalnaté Pleso* (CAOSP).

## Headline result

On a fixed final-strict sample of 356 stars (Gaia astrometric quality +
1 arcsec LAMOST DR9 LRS cross-match + Gaia–LAMOST RV consistency), the
count of likely unbound stars under the galpy `MWPotential2014` Galactic
potential changes as follows when only the distance estimator is varied:

| threshold | inverse parallax | Bailer-Jones |
|---|---:|---:|
| `P_unbound > 0.5` | **48** | **3** |
| `P_unbound > 0.7` | 29 | 1 |
| `P_unbound > 0.9` | **12** | **1** |

45 stars are downgraded across `P_unbound = 0.5` and none are gained.
Substituting LAMOST radial velocities for Gaia radial velocities on the
same sample changes the median Galactocentric speed by 0.00 km/s and
flips the classification of one star. The unbound classification is
therefore distance-dominated, not RV-dominated.

## Repository layout

```
caosp-hivel-pipeline/
├── manuscript/           # CAOSP LaTeX source + compiled PDF + cover letter
├── scripts/              # 00–08 numbered pipeline entry points
├── src/caosp_hivel/      # library code (TAP, kinematics, cross-match …)
├── config/               # YAML knobs (rates, fields, catalogue ids)
├── tests/                # pytest including the source_id integrity guard
├── reports/              # methodology & QC notes that the paper cites
├── data/processed/       # small CSVs referenced from the paper (large
│                         # parquet products are .gitignored)
└── paper/                # auto-generated figure & table artefacts
```

## How to reproduce the paper

```bash
# 1) Python 3.10+ environment
python -m venv .venv && source .venv/Scripts/activate    # Windows: .venv\Scripts\activate.bat
pip install -e .[dev]

# 2) Public data fetches
python scripts/00_check_env.py
python scripts/01_fetch_vizier_hivel_catalogs.py     # VizieR (small)
python scripts/02_fetch_gaia_dr3_fields.py           # Gaia archive (uploads chunks)

# 3) LAMOST DR9 LRS catalogue (~2 GB; not redistributed in this repo)
#    Download the public DR9 v2.0 LRS stellar-parameter catalogue manually
#    and place it under data/external/lamost/dr9_v2.0_LRS_stellar.csv.gz
python scripts/05_lamost_crossmatch.py

# 4) Sample definition + Bailer-Jones distance + final kinematics + figs
python scripts/04A_build_gaia_master_qc.py
python scripts/04B_kinematics_mc.py
python scripts/04D_bailer_jones_distance.py
python scripts/06_define_final_sample.py
python scripts/06B_final_kinematics.py
python scripts/06C_same_sample_distance_sensitivity.py
python scripts/07_paper_figures_tables.py

# 5) Compile the manuscript (requires TeX Live)
cd manuscript && bash build.sh
```

## Compliance rules

The pipeline enforces, via `src/caosp_hivel/net.py`:

- ≤ 1 request/s per external host (configurable in `config/settings.yaml`);
- polite `User-Agent` with a contact address;
- exponential-backoff retries through `tenacity`;
- resumable runs: cached outputs are skipped, TAP async jobs are
  persisted in `cache/tap_jobs.json`;
- no browser emulation, proxy pools, CAPTCHA bypass, or full-archive
  dumps. The Gaia full source table and LAMOST spectra are never
  downloaded.

## Citing this work

If you use this code or the supplementary CSV in published work, please
cite the manuscript above (CAOSP DOI to be assigned) and acknowledge the
upstream archives (Gaia DPAC, LAMOST, VizieR) following
[`CITATION.md`](CITATION.md).

## License

MIT — see [`LICENSE`](LICENSE). Catalogues fetched from VizieR, the Gaia
archive and LAMOST remain governed by their own distribution terms.
