# Catalog source provenance

Authoritative record of the three high-velocity-star catalogues consumed by
the pipeline, including which sub-table is canonical and why.

> **Naming-correction note.** An earlier draft of this project labelled the
> middle catalogue `zhao2023`. That label was wrong — the catalogue is
> Li+ 2023. The label has been changed to `li2023` everywhere
> (`config/catalogs.yaml`, `data/raw/vizier/`, `data/raw/gaia/`,
> the master CSV's `catalogs` column).

---

## 1. li2021 — `J/ApJS/252/3`

| field | value |
|---|---|
| VizieR id | `J/ApJS/252/3` |
| Title | High-velocity stars in the Galactic halo from LAMOST & Gaia |
| Authors | Li Y.-B., Luo A.-L., Lu Y.-J., Zhao Y.-H., et al. |
| Year | 2021 |
| Journal | ApJS, 252, 3 |
| Sub-table used | `J/ApJS/252/3/hivelscs` (table[0]) |
| Row count (VizieR) | **591** |
| Gaia DR3 hits | 581 (10 missing — see QC §2) |
| Key columns | `Gaia` (DR3 source_id, integer), `RA_ICRS`, `DE_ICRS`, `S/N`, `SpT`, `RV`, `pmRA`, `pmDE`, `plx`, `RPmag`, `Astro`, `RVc`, `Dist`, `X/Y/Z`, `rGC`, `Vx/Vy/Vz`, `Vgc`, `e` (eccentricity), `Zmax`, `Rmin` |
| Notes | Catalogue is single-table; `Gaia` column is plain `int64`. |

---

## 2. li2023 — `J/AJ/166/12`

| field | value |
|---|---|
| VizieR id | `J/AJ/166/12` |
| Title | Velocity data for 88 very high velocity stars |
| Authors | Li Q.-Z., Luo A.-L., Yang H.-F., et al. |
| Year | 2023 |
| Journal | AJ, 166, 12 |
| Sub-table used | **`J/AJ/166/12/table5`** (the 88-row Table A1) |
| Row count (VizieR) | **88** |
| Gaia DR3 hits | 88 |
| Key columns | `ID`, `HVS`, `Name`, `Gaia` (DR3 source_id, integer), `RAJ2000`, `DEJ2000`, `pmRA`, `e_pmRA`, `pmDE`, `e_pmDE`, `Vlos`, `e_Vlos`, `Dist`, `e_Dist`, `Teff`, `e_Teff`, `logg`, `e_logg` |

### Why 88 and not 52?

This VizieR record contains **four sub-tables**; the difference between them
is exactly the kind of detail a reviewer will probe.

| sub-table | rows | description |
|---|---:|---|
| `table2` | 52 | HVS candidates **after** applying escape-velocity-curve filtering |
| `table3` | 8 | HiVel passing within 1 kpc of the Galactic centre |
| `table4` | 15 | extreme-velocity stars probably originating from Sgr dSph |
| **`table5` (Table A1)** | **88** | **full list of HVSs or candidates** — the published parent sample |

Earlier in this project the canonical table was inadvertently set to
`table[0]` (= `table2`, 52 rows) because that is what `astroquery.vizier`
returns first. The pipeline now selects `table5` explicitly via the new
`table:` key in `config/catalogs.yaml`, so the master sample contains the
**88-row parent population, not the 52-row escape-velocity-filtered subset**.

If a downstream analysis specifically needs the 52-star or 8-star or 15-star
sub-cuts, they remain on disk at
`data/raw/vizier/li2023__t0.parquet` (52),
`li2023__t1.parquet` (8),
`li2023__t2.parquet` (15) respectively.

---

## 3. liao2024 — `J/AJ/167/76`

| field | value |
|---|---|
| VizieR id | `J/AJ/167/76` |
| Title | Catalog of 519 high velocity stars (HiVels) considering the impact of the Large Magellanic Cloud |
| Authors | Liao Y., Lu Y.-J., Luo A.-L., et al. |
| Year | 2024 |
| Journal | AJ, 167, 76 |
| Sub-table used | `J/AJ/167/76/table6` (table[0]) |
| Row count (VizieR) | **519** |
| Gaia DR3 hits | 519 |
| Key columns | `Gaia` (DR3 source_id, **as the string** `"Gaia DR3 <id>"`), `RAICRS`, `DEICRS`, `plx`, `pmRA`, `pmDE`, `Gmag`, `BP-RP`, `Teff`, `logg`, `[Fe/H]`, `RVel`, `Dist`, `VGC`, `_RA.icrs`, `_DE.icrs` |
| Notes | The `Gaia` column is **a string with the prefix `"Gaia DR3 "`**, not a bare integer. The pipeline strips the prefix in `scripts/02_fetch_gaia_dr3_fields.py` via the regex `(\d{6,})`. |

---

## 4. Summary

| label | catalog id | sub-table | rows | reference |
|---|---|---|---:|---|
| li2021 | J/ApJS/252/3 | hivelscs | 591 | Li Y.-B. et al. 2021, ApJS 252, 3 |
| li2023 | J/AJ/166/12 | table5 (= Table A1) | 88 | Li Q.-Z. et al. 2023, AJ 166, 12 |
| liao2024 | J/AJ/167/76 | table6 | 519 | Liao Y. et al. 2024, AJ 167, 76 |
| **union** | — | — | **1198** (1188 with Gaia DR3, 1101 unique source_ids) | — |

Pairwise overlaps (after Gaia DR3 resolution): see `gaia_vizier_qc.md` §3.
