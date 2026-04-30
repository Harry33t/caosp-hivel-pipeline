# Gaia × VizieR master sample QC report

Generated automatically by `scripts/04A_build_gaia_master_qc.py`.

## 1. Per-catalogue counts

| catalog | VizieR rows | Gaia DR3 hit | missing |
|---|---:|---:|---:|
| li2021 (J/ApJS/252/3) | 591 | 581 | 10 |
| li2023 (J/AJ/166/12) | 88 | 88 | 0 |
| liao2024 (J/AJ/167/76) | 519 | 519 | 0 |

## 2. li2021 missing source_ids (10)

These VizieR `Gaia` ids returned no row from `gaiadr3.gaia_source`. Most likely they were merged or removed between EDR3 and DR3.

```
307484203439532928
660993856243314176
1267516459040509056
1563756085910081664
1597988246569491968
1610635344708272512
1623040073548211840
3599497367907792256
4422830744441142784
4561622303376290688
```

## 3. Pairwise & triple overlaps (Gaia hits)

| pair | shared sources |
|---|---:|
| li2021 ∩ li2023 | 12 |
| li2021 ∩ liao2024 | 75 |
| li2023 ∩ liao2024 | 0 |
| all three | 0 |

## 4. Duplicate diagnostics (master table)

- master rows (unique source_id): **1101**
- duplicated source_id: **0** (should be 0)
- duplicate (ra, dec) rounded to 1e-6 deg: **0 rows in 0 groups**

## 5. Missing-value counts in master table

Total rows = 1101.

| field | NaN count | NaN % |
|---|---:|---:|
| parallax | 0 | 0.0% |
| parallax_error | 0 | 0.0% |
| parallax_over_error_NaN | 0 | 0.0% |
| radial_velocity | 317 | 28.8% |
| radial_velocity_error | 317 | 28.8% |
| phot_g_mean_mag | 0 | 0.0% |
| phot_bp_mean_mag | 0 | 0.0% |
| phot_rp_mean_mag | 0 | 0.0% |
| ruwe | 0 | 0.0% |

## 6. RUWE distribution

| quantile | RUWE |
|---|---:|
| 25% | 0.98 |
| 50% | 1.018 |
| 75% | 1.066 |
| 90% | 1.162 |
| 99% | 2.316 |

## 7. Filter counts

| filter | count | %% of master |
|---|---:|---:|
| ruwe < 1.4 | 1071 | 97.3% |
| parallax_over_error > 5 | 977 | 88.7% |
| radial_velocity not null | 784 | 71.2% |
| all three above | 675 | 61.3% |

## 8. Output files

- `data\processed\hivel_gaia_master.parquet`
- `data\processed\hivel_gaia_master.csv`
