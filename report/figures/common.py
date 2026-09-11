"""Shared loaders and style for the IEEE-paper figures.

Every figure script imports from here.  All data is read from the repository's
own result files (paths below); nothing is typed in by hand.  Run any
``make_*.py`` from anywhere; paths are resolved relative to this file.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # git-checkout/
RESULTS = ROOT / "results"
RUNS = RESULTS / "runs"
EVIDENCE = ROOT / "evidence"
OUT = HERE                                   # PDFs are written next to the scripts

# IEEE column geometry (inches)
COL_W = 3.45
PAGE_W = 7.16

# Condition naming: config name -> paper short name, fixed categorical order.
COND_ORDER = ["baza", "tokenizator", "transplant_mean", "transplant_random_coef",
              "turk", "her_ikisi", "turk_qarisiq"]
COND_LABEL = {
    "baza": "Direct", "tokenizator": "OMP", "transplant_mean": "Mean",
    "transplant_random_coef": "Random", "turk": "TR", "her_ikisi": "OMP+TR",
    "turk_qarisiq": "Shuf. TR",
}
# Validated categorical palette (dataviz reference instance, fixed slot order).
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
COND_COLOR = {c: PALETTE[i] for i, c in enumerate(COND_ORDER)}
COND_MARKER = {"baza": "o", "tokenizator": "s", "transplant_mean": "^",
               "transplant_random_coef": "v", "turk": "D", "her_ikisi": "P", "turk_qarisiq": "X"}
BASE_LABEL = {"xlm15": "XLM-15", "xlmr": "XLM-R"}
BASE_ORDER = ["xlm15", "xlmr"]
GRAY = "#52514e"
LIGHT_GRAY = "#d9d8d3"
ESCAPE_THRESHOLD = 0.40
COLLAPSE_F1 = 1 / 3  # macro-F1 of a constant predictor on a balanced binary split


def style() -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": GRAY, "axes.labelcolor": "#0b0b0b",
        "xtick.color": GRAY, "ytick.color": GRAY,
        "axes.grid": True, "grid.color": LIGHT_GRAY, "grid.linewidth": 0.4,
        "axes.axisbelow": True, "lines.linewidth": 1.2,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    })


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_runs() -> list[dict]:
    """All 164 schema-v4 run records."""
    files = sorted(glob.glob(str(RUNS / "*.json")))
    out = [load_json(Path(f)) for f in files]
    assert len(out) == 164, len(out)
    assert all(r.get("run_result_schema_version") == 4 for r in out)
    return out


def load_aggregate() -> pd.DataFrame:
    df = pd.read_csv(RESULTS / "aggregate.csv")
    assert len(df) == 164
    return df


def load_summary() -> pd.DataFrame:
    df = pd.read_csv(RESULTS / "summary.csv")
    for col in ("escape_rate_wilson_ci", "conditional_macro_f1_bootstrap_ci",
                "all_seed_macro_f1_bootstrap_ci"):
        df[col] = df[col].apply(lambda s: json.loads(s) if isinstance(s, str) else [None, None])
    assert len(df) == 36
    return df


def load_stats() -> pd.DataFrame:
    df = pd.read_csv(RESULTS / "stats.csv")
    df["survives_family_correction"] = df["survives_family_correction"].fillna(False).astype(bool)
    assert len(df) == 96
    return df


def parse_test_tables() -> dict[str, pd.DataFrame]:
    """Parse the markdown tables T1, T2, T5 of the full received test-table file."""
    path = EVIDENCE / "supplemental" / "test_tables_received.md"
    text = path.read_text(encoding="utf-8")
    tables: dict[str, pd.DataFrame] = {}
    cur, rows, header = None, [], None
    for line in text.splitlines():
        if line.startswith("## "):
            if cur and rows:
                tables[cur] = pd.DataFrame(rows, columns=header)
            cur = line[3:5].strip()
            rows, header = [], None
            continue
        if line.startswith("|") and cur:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                header = cells
            elif set(line.replace("|", "").strip()) <= set("-: "):
                continue
            else:
                rows.append(cells)
    if cur and rows:
        tables[cur] = pd.DataFrame(rows, columns=header)
    return tables


def _ci(text: str) -> tuple[float, float, float]:
    """'0.7783 [0.7728, 0.7854]' -> (0.7783, 0.7728, 0.7854)"""
    val, rest = text.split("[")
    lo, hi = rest.rstrip("]").split(",")
    return float(val), float(lo), float(hi)


def load_test_cells() -> pd.DataFrame:
    """Per-cell test macro-F1 (T1) with CIs, typed."""
    t1 = parse_test_tables()["T1"]
    recs = []
    for _, r in t1.iterrows():
        c, clo, chi = _ci(r["Test F1 (conditional, escaped only) [95% CI]"])
        a, alo, ahi = _ci(r["Test F1 (all-seed) [95% CI]"])
        recs.append(dict(base=r["Base"], condition=r["Condition"], train_size=int(r["n"]),
                         test_cond=c, test_cond_lo=clo, test_cond_hi=chi,
                         test_all=a, test_all_lo=alo, test_all_hi=ahi))
    return pd.DataFrame(recs)


def save(fig, name: str) -> None:
    out = OUT / name
    fig.savefig(out)
    print("wrote", out)
