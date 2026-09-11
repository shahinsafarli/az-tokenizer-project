# IEEE paper build (`report/ieee/`)

Self-contained IEEEtran (conference) source of the final report. Nothing here is
typed in by hand from results: every figure and every numeric table is regenerated
from the repository's result files by the scripts below.

```
report.tex            IEEEtran preamble + author block + section includes
sections/*.tex        paper text (00_abstract … 11_appendix)
refs.bib              bibliography (IEEEtran.bst)
figures/common.py     shared loaders / style (paths resolve to ../../results, ../../evidence)
figures/make_*.py     one script per figure  -> figures/fig_*.pdf (vector)
figures/fig_design.tex TikZ design schematic (counts only)
tables/make_tables.py all numeric tables     -> tables/tab_*.tex (each with a "% source:" header)
build.ps1 / build.sh  regenerate figures + tables, then latexmk -pdf
report.pdf            compiled output (26 pages)
```

## Build

Windows (MiKTeX installed under `%LOCALAPPDATA%\Programs\MiKTeX`):

```powershell
.\build.ps1
```

POSIX (TeX Live / MiKTeX with `latexmk` on PATH):

```bash
bash build.sh
```

Requirements: Python 3.10+ with `matplotlib`, `numpy`, `pandas`, `scipy`; a LaTeX
distribution with `IEEEtran`, `newtx`, `booktabs`, `algorithm2e`, `tikz`,
`newunicodechar`, `threeparttable`, `stfloats`, `hyperref`.

Note for MiKTeX + `latexmk -outdir=build`: BibTeX needs `BIBINPUTS` to include this
directory (`build.ps1` sets it).

## Figure / table provenance

| Artefact | Script | Source files (relative to repo root) |
|---|---|---|
| Fig. 1 design | `figures/fig_design.tex` | `evidence/preregistration/FROZEN.md`, `results/launcher_state.json` (counts only) |
| Fig. 2 runtime | `make_fig_errors_runtime.py` | `results/aggregate.csv` |
| Fig. 3 tokenizer | `make_fig_tokenizer.py` | `results/overlap_control.json`, `results/truncation.json` |
| Fig. 4 intrinsic | `make_fig_intrinsic.py` | `results/anchors.json`, `top1_accuracy.json`, `cross_base_transplant_quality.json`, `embedding_norm_report__*.json` |
| Fig. 5 trajectories | `make_fig_trajectories.py` | `results/runs/*__n=2000__*.json` (`step_history`) |
| Fig. 6 escape | `make_fig_escape.py` | `results/runs/*.json` |
| Fig. 7 summary | `make_fig_summary.py` | `results/summary.csv`, `evidence/supplemental/test_tables_received.md` (T1) |
| Fig. 8 forest | `make_fig_forest.py` | `results/stats.csv`, `results/runs/*.json` |
| Fig. 9 sign-flip | `make_fig_signflip.py` | `results/runs/*xlmr*__n=2000__*.json` |
| Fig. 10 Turkish | `make_fig_turkish.py` | `results/aggregate.csv` |
| Fig. 11 val/test | `make_fig_valtest.py` | `results/aggregate.csv`, `test_tables_received.md` (T2) |
| Fig. 12 errors | `make_fig_errors_runtime.py` | `results/errors.json` |
| Tables IV, V, X, XII–XX, XXIII, XXIV, XXVI (numeric) | `tables/make_tables.py` | header comment of each `tables/tab_*.tex` |
| Tables I–III, VI–IX, XI, XXI, XXV (hand-written) | `sections/*.tex` | values cited to files in each caption |
