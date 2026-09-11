#!/usr/bin/env bash
# Build the IEEE paper: regenerate figures + tables from result files, then latexmk.
set -euo pipefail
cd "$(dirname "$0")"
python figures/make_fig_tokenizer.py
python figures/make_fig_intrinsic.py
python figures/make_fig_trajectories.py
python figures/make_fig_escape.py
python figures/make_fig_summary.py
python figures/make_fig_forest.py
python figures/make_fig_valtest.py
python figures/make_fig_turkish.py
python figures/make_fig_errors_runtime.py
python figures/make_fig_signflip.py
python tables/make_tables.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build report.tex
cp build/report.pdf report.pdf
echo "built report.pdf ($(python -c "import fitz;print(len(fitz.open('report.pdf')))" 2>/dev/null || echo '?') pages)"
