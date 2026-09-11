# Cross-lingual Transfer between Azerbaijani and Turkish

This repository contains the code, frozen configuration, tests, results, and
submission artifacts for a controlled study of two adaptation routes for
Azerbaijani sentiment classification:

1. intermediate training on related-language Turkish data; and
2. replacement of the base tokenizer with an Azerbaijani donor tokenizer whose
   embeddings are reconstructed without additional pretraining.

The study compares seven conditions across two multilingual encoders, four
Azerbaijani training sizes, and multiple seeds. The completed evidence set
contains 164 runs.

## Repository contents

- `src/` - data preparation, tokenization, transplant, training, and analysis code
- `configs/` - frozen experiment configuration and SHA-256 lock file
- `resources/` - domain keywords and false-friend resources
- `tests/` - offline unit and integration tests
- `results/` - aggregate results, statistical tests, and diagnostic outputs
- `figures/` and `tables/` - principal generated findings
- `evidence/results_full.zip` - all 164 run JSON files and 164 execution logs
- `report/` - IEEE LaTeX source, bibliography, figures, tables, and final PDF
- `presentation/presentation.pdf` - final presentation
- `contribution_report.pdf` - team contribution statement

## Environment

Python 3.10 or later is required. Create an isolated environment and install the
locked dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
```

## Data and model sources

The experiment configuration downloads the following public model and dataset
resources from Hugging Face:

- Azerbaijani data: `LocalDoc/sentiments_dataset_azerbaijani`,
  CC-BY-NC-SA-4.0
- Turkish data: `maydogan/Turkish_SentimentAnalysis_TRSAv1`; the captured dataset
  card declares no licence, so dataset rows are not redistributed here
- Primary encoder: `FacebookAI/xlm-mlm-tlm-xnli15-1024`, CC-BY-NC-4.0
- Contrast encoder: `xlm-roberta-base`, MIT
- Donor: `HPLT/hplt_bert_base_az`, Apache-2.0, pinned to revision
  `a126552c30733333cc95425b4eefd3d85b39d878`

The Azerbaijani dataset revision used by the configuration is unpinned. A fresh
download must match the train, validation, and test content hashes recorded in
`results/splits.json` before it is treated as the same dataset. The original raw
text snapshot is intentionally not redistributed.

## Reproduce the experiment

From the repository root, the complete experiment is launched with one command:

```bash
bash run_all.sh
```

This command prepares the data, constructs transplant and control variants,
runs the training grid, and regenerates aggregate statistics, tables, and
figures. It downloads external datasets and models and performs the full
training workload.

Existing results can be inspected without training. First verify and extract the
run archive:

```bash
(cd evidence && sha256sum -c results_full.sha256)
unzip evidence/results_full.zip -d .
bash run_all.sh --analysis-only
```

The expected archive SHA-256 is:

```text
29e9d7406950d0bb28535a894cc351b8e209a6c3a9f1a475e4cf32d4e169a390
```

## Tests

The offline test suite does not download models or datasets:

```bash
python -m pytest -q -m "not slow"
```

The validated repository state passes 90 tests, with one slow test deselected.

## Principal result

For XLM-R at 2,000 Azerbaijani training examples, the implemented OMP tokenizer
transplant reduced validation macro-F1 from 0.8277 to 0.7618 and test macro-F1
from 0.7970 to 0.7404. Turkish intermediate training was numerically strongest,
but its gains over direct fine-tuning did not survive correction over the full
declared statistical family. The report documents the collapse behaviour,
statistical limits, and all qualifications.

## Submission artifacts

- Final paper: `report/report.pdf`
- Paper source archive: `report/ieee_source.rar`
- Final presentation: `presentation/presentation.pdf`
- Contribution statement: `contribution_report.pdf`
- Repository release: `v1.0-final`

## Team

- Fatima Alibabayeva - `FatimaAlibabayeva`
- Suleyman Allahverdiyev - `SuleymanAllahverdiyev`
- Fidan Baghirova - `Fidan6557`
- Emil Jafarov - `Emil-Jafarov-06`
- Shahin Safarli - `shahinsafarli`

