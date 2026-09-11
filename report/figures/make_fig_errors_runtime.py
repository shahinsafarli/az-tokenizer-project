"""Two column-width figures.

fig_errors.pdf  : automatic error taxonomy on test predictions at n = 2,000, per condition,
                  pooled over both bases and all seeds (41,860 evaluated predictions per condition)
                  <- results/errors.json
fig_runtime.pdf : per-run wall-clock (runtime_sec) by base and condition, one stream throughout
                  <- results/aggregate.csv
"""
import matplotlib.pyplot as plt
import numpy as np

from common import (BASE_LABEL, COL_W, COND_COLOR, COND_LABEL, COND_ORDER, GRAY, PALETTE, RESULTS,
                    load_aggregate, load_json, save, style)

style()

# ---------------------------------------------------------------- errors
err = load_json(RESULTS / "errors.json")
cats = ["morfoloji", "texniki_lugat", "yalanci_dost", "diger"]
cat_label = {"morfoloji": "morphological", "texniki_lugat": "technical vocabulary",
             "yalanci_dost": "false friend", "diger": "other"}
cat_col = {"morfoloji": PALETTE[0], "texniki_lugat": PALETTE[1], "yalanci_dost": PALETTE[7], "diger": "#bcbab3"}

fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.8), gridspec_kw={"width_ratios": [1, 1.1]})
ax = axes[0]
rates = [err["conditions"][c]["error_rate_pct"] for c in COND_ORDER]
bb = ax.bar(range(7), rates, color=[COND_COLOR[c] for c in COND_ORDER], width=0.65)
for b_, v in zip(bb, rates):
    ax.text(b_.get_x() + b_.get_width() / 2, v + 0.4, f"{v:.1f}", ha="center", va="bottom", fontsize=5.6)
ax.set_xticks(range(7), [COND_LABEL[c] for c in COND_ORDER], rotation=45, ha="right", fontsize=6)
ax.set_ylabel("test error rate (%)")
ax.set_ylim(0, 40)
ax.set_title("(a) Errors, $n$ = 2,000, both bases", loc="left")
ax.grid(axis="x", visible=False)

ax = axes[1]
bottom = np.zeros(7)
for cat in cats:
    vals = np.array([err["conditions"][c]["shares_pct"][cat] for c in COND_ORDER])
    ax.bar(range(7), vals, bottom=bottom, color=cat_col[cat], width=0.65, label=cat_label[cat],
           edgecolor="white", linewidth=0.4)
    bottom += vals
ax.set_xticks(range(7), [COND_LABEL[c] for c in COND_ORDER], rotation=45, ha="right", fontsize=6)
ax.set_ylabel("share of errors (%)")
ax.set_ylim(0, 100)
ax.set_title("(b) Keyword category", loc="left")
ax.legend(frameon=False, fontsize=5.5, loc="upper right", bbox_to_anchor=(1.02, 0.98), handlelength=1.0)
ax.grid(axis="x", visible=False)
fig.tight_layout(w_pad=0.8)
save(fig, "fig_errors.pdf")

# ---------------------------------------------------------------- runtime
agg = load_aggregate()
fig, ax = plt.subplots(figsize=(COL_W, 1.9))
rng = np.random.default_rng(1)
x = 0
ticks, labels = [], []
for b in ("xlm15", "xlmr"):
    for c in COND_ORDER:
        s = agg[(agg.base == b) & (agg.condition == c)]
        jit = rng.uniform(-0.2, 0.2, len(s))
        sizes = s.train_size.map({500: 6, 2000: 9, 10000: 13, 20914: 17})
        ax.scatter(x + jit, s.runtime_sec / 60, s=sizes, color=COND_COLOR[c], linewidths=0.3, edgecolors="white",
                   alpha=0.85)
        ax.plot([x - 0.3, x + 0.3], [s.runtime_sec.median() / 60] * 2, color="#0b0b0b", lw=0.8)
        ticks.append(x); labels.append(COND_LABEL[c].replace("Shuf. TR", "Shuf.").replace("OMP+TR", "OMP\n+TR"))
        x += 1
    x += 0.8
ax.set_xticks(ticks, [l.replace("\n", " ") for l in labels], fontsize=5.5, rotation=45, ha="right")
ax.set_ylabel("run wall-clock (min)")
ax.set_ylim(0, 8)
ax.text(3, 7.6, BASE_LABEL["xlm15"] + " (94 runs)", ha="center", fontsize=6.5, color=GRAY)
ax.text(10.8, 7.6, BASE_LABEL["xlmr"] + " (70 runs)", ha="center", fontsize=6.5, color=GRAY)
ax.text(0.99, 0.03, "marker size grows with $n$ (500 … 20,914); bar = median", transform=ax.transAxes, ha="right",
        va="bottom", fontsize=5.5, color=GRAY)
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "fig_runtime.pdf")
