# Manuscript

LaTeX source of the paper *A Gaia DR3--LAMOST reassessment of high-velocity
star candidates with geometric-distance-aware kinematics*.

## Layout

```
manuscript/
├── manuscript.tex         # main source
├── references.bib         # 40 BibTeX entries
├── reference_usage_plan.md# section-by-section assignment of refs
├── caosp310.cls           # journal class (CAOSP, copy of upstream)
├── caosp310.bst           # bibliography style
├── logo_orcid.pdf         # required by the \orcid command
├── figures/               # 7 figure PDFs from the pipeline
└── tables/                # 3 tabular fragments \input-ed by manuscript.tex
```

## Build

```bash
bash build.sh
```

(or manually: `pdflatex` → `bibtex` → `pdflatex` × 2.)

Output: `manuscript.pdf`.

## Regenerating figures and tables

The figures and tables originate from the companion repository
`../caosp-hivel-pipeline/`:

```bash
cd ../caosp-hivel-pipeline
.venv/Scripts/python.exe scripts/07_paper_figures_tables.py
.venv/Scripts/python.exe scripts/_strip_table_wrappers.py
.venv/Scripts/python.exe scripts/_unicode_to_latex_in_tables.py
```

The strip + unicode steps copy the LaTeX-ready fragments into
`./tables/`; the figure PDFs need to be copied manually with

```bash
cp ../caosp-hivel-pipeline/paper/figures/*.pdf ./figures/
```

## Notes on the CAOSP class

- `caosp310.cls` requires the placeholder editorial fields
  (`\articleNo`, `\pubyear`, `\volume`, `\volnumber`, `\firstpage`,
  `\received`, `\accepted`); they are filled at acceptance time.
- The class injects ASCII letter-spaced headings; non-ASCII characters
  in section/caption titles must be wrapped in `\ensuremath{...}`
  for math symbols, or rewritten with `\textgreek` /
  appropriate substitutes. The companion script
  `_unicode_to_latex_in_tables.py` handles this for the auto-generated
  tabular fragments.
- The `\orcid` command pulls `logo_orcid.pdf` from the working
  directory; if you remove the orcid line, that file is no longer needed.
