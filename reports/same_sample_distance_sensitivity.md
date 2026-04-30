# Same-sample distance sensitivity (Step 6C)

All numbers below are computed on **the same `sample_final_strict` of 356 stars**. The two passes differ only in the distance estimator: inverse parallax ($1000/\varpi$) vs Bailer-Jones geometric distance ($r_{\mathrm{med,geo}}$ from `external.gaiaedr3_distance`). Proper motions, Gaia DR3 radial velocities, and the Monte Carlo error budget are otherwise identical (1000 draws per star).

## 1. Counts of unbound candidates on the same 356-star sample

| threshold | inverse parallax | Bailer-Jones | net change |
|---|---:|---:|---:|
| $P_{\rm unbound} > 0.5$ | 48 | 3 | -45 |
| $P_{\rm unbound} > 0.7$ | 29 | 1 | -28 |
| $P_{\rm unbound} > 0.9$ | 12 | 1 | -11 |

Sample size: **N = 356**.

## 2. Per-star reclassification

| transition (across $P_{\rm unbound}=0.5$) | count |
|---|---:|
| inverse-parallax $>0.5$ $\rightarrow$ Bailer-Jones $\le 0.5$ (downgraded) | 45 |
| inverse-parallax $\le 0.5$ $\rightarrow$ Bailer-Jones $>0.5$ (promoted)   | 0 |

## 3. Distance ratio on the same sample

- median $r_{\rm med,geo}/(1000/\varpi)$ (full strict, N=356): **0.850**
- median ratio on stars with inverse-parallax $P_{\rm unbound}>0.5$: **0.756**

## 4. Headline statement (replaces previous master-vs-strict mix)

> On the same final-strict sample of 356 stars, replacing inverse-parallax distances with Bailer-Jones geometric distances reduces the number of likely unbound candidates ($P_{\rm unbound}>0.5$) from **48** to **3**, and the number of high-confidence unbound candidates ($P_{\rm unbound}>0.9$) from **12** to **1**. The distance estimator alone---not the LAMOST quality or RV-consistency cuts---is responsible for the change.

## 5. Outputs

- `data\processed\same_sample_distance_sensitivity.csv` (one row per source, both passes side-by-side)
- This report.
