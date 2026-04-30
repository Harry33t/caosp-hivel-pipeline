#!/usr/bin/env bash
# Build the manuscript PDF.
#
# Run from the manuscript/ directory:
#     bash build.sh
#
# Requires TeX Live (pdflatex, bibtex). The CAOSP class file
# caosp310.cls and the bibliography style caosp310.bst sit in this folder.

set -euo pipefail

# 1. First pass — generates manuscript.aux with citation keys.
pdflatex -interaction=nonstopmode manuscript.tex >/dev/null

# 2. BibTeX — resolves \cite{} against references.bib and writes manuscript.bbl.
bibtex manuscript >/dev/null

# 3. Two more pdflatex passes — first to incorporate .bbl, second to settle
#    cross-references (figures, tables, sections) and the running headings.
pdflatex -interaction=nonstopmode manuscript.tex >/dev/null
pdflatex -interaction=nonstopmode manuscript.tex >/dev/null

echo "Built: $(ls -lh manuscript.pdf | awk '{print $5,$9}')"
