# source_id integrity audit

Trigger: the user noticed the Top-1 and Top-2 Gaia DR3 source_id in
`paper/tables/table3_final_top_candidates.tex` ended in different digits than
the same Top-1/Top-2 in `data/processed/final_top_candidates.csv` and the
parquet master tables. A 19-digit Gaia DR3 source_id exceeds the 53-bit
mantissa of a 64-bit IEEE-754 float (≈15.95 decimal digits), so any code path
that silently routes the integer through `float64` truncates the trailing
3–4 digits.

## 1. Audit scope

Every file that reads or writes a `source_id` column was inspected:

| location | mode | source_id dtype | verdict |
|---|---|---|---|
| `src/caosp_hivel/gaia.py` (TAP upload) | `Table({"source_id": ids})` | `int64` (astropy) | OK |
| `src/caosp_hivel/lamost.py` | `pd.read_csv(usecols=...)` then merge | `int64` | OK |
| `scripts/02_fetch_gaia_dr3_fields.py` | extracted via `pd.to_numeric(..., int64)` | `int64` | OK |
| `scripts/04A_build_gaia_master_qc.py` | `master["source_id"].astype("int64")` | `int64` | OK |
| `scripts/04B_kinematics_mc.py` | `int(r.source_id)` per row | `int64` (CPython int is exact) | OK |
| `scripts/04D_bailer_jones_distance.py` | TAP join on `source_id` | `int64` | OK |
| `scripts/05_lamost_crossmatch.py` | numpy `iloc[idx_g].values` | `int64` | OK |
| `scripts/06_define_final_sample.py` | parquet pass-through | `int64` | OK |
| `scripts/06B_final_kinematics.py` | parquet → DataFrame → CSV | `int64`; **CSV: int64 in text form** | OK in CSV, but unprotected |
| **`scripts/07_paper_figures_tables.py`** | `"{:.0f}".format(v)` on `source_id` | **`int64` → `float64` (lossy)** | **BUG** |

All parquet, intermediate CSV and raw VOTable artefacts kept `int64`
throughout. The corruption was confined to the LaTeX output of Table 3.

## 2. Root cause

In `scripts/07_paper_figures_tables.py::table3_top` we declared the formatter
for the source_id column as `"{:.0f}"`. Python's `str.format` with the `f`
type spec coerces its argument to a float before printing — even when the
argument is a Python `int`. For 19-digit Gaia source_ids this drops the last
3–4 digits.

Concretely:
```python
>>> "{:.0f}".format(1383279090527227264)
'1383279090527227392'
```

`pandas.DataFrame.to_latex` itself was not at fault — it was given the
already-corrupted strings that our formatter produced.

## 3. Diff: parquet truth vs LaTeX output (before fix)

17 / 30 Top candidates had a corrupted source_id in `table3_final_top_candidates.tex`.

| rank | parquet (truth) | LaTeX (broken) | low-bit Δ |
|---:|---|---|---:|
| 1 | 1383279090527227264 | 1383279090527227**392** | +128 |
| 2 | 1204061267883975040 | 1204061267883975**168** | +128 |
| 3 | 3877058564258758656 | 3877058564258758656 | 0 |
| 4 | 1375165725506487424 | 1375165725506487**296** | −128 |
| 5 | 2105847208541125248 | 2105847208541125**120** | −128 |
| 6 | 4450458649852400640 | 4450458649852400640 | 0 |
| 7 | 1477675943342041472 | 1477675943342041**600** | +128 |
| 8 | 1297316350890352000 | 1297316350890352**128** | +128 |
| 9 | 3960007851762445696 | 3960007851762445**824** | +128 |
| 10 | 3651065597121243648 | 3651065597121243648 | 0 |
| 11 | 1480182073940289024 | 1480182073940289024 | 0 |
| 12 | 4429980078286167424 | 4429980078286167**552** | +128 |
| 13 | 3696393857329932672 | 3696393857329932**800** | +128 |
| 14 | 2125719266307162240 | 2125719266307162**112** | −128 |
| 15 | 1850497933774341504 | 1850497933774341**632** | +128 |
| 16 | 4467979165785261824 | 4467979165785262**080** | +256 |
| 17 | 802937337058585344  | 802937337058585344  | 0 |
| 18 | 125510837155597696  | 125510837155597696  | 0 |
| 19 | 1298337316156102144 | 1298337316156102144 | 0 |
| 20 | 4547925480869924096 | 4547925480869923**840** | −256 |
| 21 | 1158126425149936384 | 1158126425149936384 | 0 |
| 22 | 2123569205674089856 | 2123569205674089**984** | +128 |
| 23 | 1282795032101821952 | 1282795032101821952 | 0 |
| 24 | 1273534017460399744 | 1273534017460399**616** | −128 |
| 25 | 3584384752382223360 | 3584384752382223360 | 0 |
| 26 | 2672173998389739264 | 2672173998389739**520** | +256 |
| 27 | 2148005748521592704 | 2148005748521592**832** | +128 |
| 28 | 4374395985929111040 | 4374395985929111040 | 0 |
| 29 | 4565070577998452096 | 4565070577998452**224** | +128 |
| 30 | 1470738952685112576 | 1470738952685112576 | 0 |

The Δ pattern (multiples of 128/256) is the float64 ULP at this magnitude
(2⁶⁰ region) — confirming the loss is a clean float64 rounding artefact, not
a different kind of corruption.

## 4. Fix

Two changes in `scripts/07_paper_figures_tables.py`:

1. In `table3_top`, cast `source_id` to a Python `str` immediately after the
   `flags` merge:
   ```python
   df["source_id"] = df["source_id"].astype("int64").astype(str)
   ```
   The format-spec for source_id is changed from `"{:.0f}"` to `None`.
2. In `_save_table`, a defensive guard auto-stringifies any integer column
   whose absolute max exceeds 2⁵³ (the largest exact-integer that float64
   can represent). This catches future tables that accidentally include a
   Gaia source_id column without explicit handling:
   ```python
   INT64_SAFE = 1 << 53
   for c in pretty.columns:
       if pd.api.types.is_integer_dtype(pretty[c]):
           if pretty[c].abs().max() > INT64_SAFE:
               pretty[c] = pretty[c].astype(str)
   ```

In `scripts/06B_final_kinematics.py`, the writer of
`data/processed/final_top_candidates.csv` was also tightened:

```python
top["source_id"] = top["source_id"].astype("int64").astype(str)
top.to_csv(out_top, index=False)
```

This keeps the CSV self-evidently a string — even if a downstream consumer
calls `pd.read_csv` with default dtype inference and pandas decides to
re-coerce a numeric-looking column to float64 for some reason.

## 5. Post-fix verification

After re-running Step 7:

```
$ grep -E "^[0-9]{19}" paper/tables/table3_final_top_candidates.tex | head -3
1383279090527227264 & li2021,liao2024 & 6.39 & 653 & ...
1204061267883975040 & liao2024        & 9.74 & 612 & ...
3877058564258758656 & liao2024        & 5.51 & 498 & ...

$ head -4 paper/tables/table3_final_top_candidates.csv
Gaia DR3 source\_id,...
1383279090527227264,"li2021,liao2024",6.387,...
1204061267883975040,liao2024,9.739,...
3877058564258758656,liao2024,5.510,...

$ head -4 data/processed/final_top_candidates.csv
source_id,catalogs,...
1383279090527227264,"li2021,liao2024",240.337,...
1204061267883975040,liao2024,238.111,...
3877058564258758656,liao2024,154.445,...
```

All three files now agree with the parquet truth on every digit.

## 6. Affected derivative files

Regenerated:
- `data/processed/final_top_candidates.csv` (source_id now string)
- `paper/tables/table3_final_top_candidates.csv`
- `paper/tables/table3_final_top_candidates.tex`
- `paper/figures/fig*.{png,pdf}` (figure 5/6 use Top-3 source_ids, but only
  via `int(...)` on the in-memory int64 — those figures were not visually
  affected; regenerated for consistency anyway)
- `paper/figure_captions.md` (no source_ids embedded; refreshed alongside)

Not affected:
- All parquet files under `data/processed/` (always `int64`)
- All raw artefacts under `data/raw/` (parquet, int64)
- `cache/bailer_jones_geo.parquet` (int64)
- All earlier-step CSV outputs that had `source_id` written as the integer
  text form by pandas default (verified by re-reading: dtype `int64`,
  byte-identical to parquet truth).

## 7. Final Top-30 source_ids (authoritative)

```
1383279090527227264   li2021,liao2024
1204061267883975040   liao2024
3877058564258758656   liao2024
1375165725506487424   li2021,liao2024
2105847208541125248   liao2024
4450458649852400640   liao2024
1477675943342041472   liao2024
1297316350890352000   liao2024
3960007851762445696   li2021,liao2024
3651065597121243648   liao2024
1480182073940289024   liao2024
4429980078286167424   liao2024
3696393857329932672   liao2024
2125719266307162240   liao2024
1850497933774341504   liao2024
4467979165785261824   liao2024
802937337058585344    liao2024
125510837155597696    liao2024
1298337316156102144   li2021,liao2024
4547925480869924096   liao2024
1158126425149936384   liao2024
2123569205674089856   liao2024
1282795032101821952   liao2024
1273534017460399744   liao2024
3584384752382223360   liao2024
2672173998389739264   liao2024
2148005748521592704   li2021,liao2024
4374395985929111040   liao2024
4565070577998452096   li2021
1470738952685112576   liao2024
```

## 8. Recommendation

Add `pytest` regression test asserting that, for every CSV/TeX deliverable
shipped to the paper, parsing back the `source_id` column matches the
parquet truth byte-for-byte. The defensive guard in `_save_table` will
automatically protect future tables, but a regression test is cheap insurance.
