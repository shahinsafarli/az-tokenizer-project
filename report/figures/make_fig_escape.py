"""Fig. escape-step distribution and the structure of collapse.

(a) escape step (first evaluation point with validation macro-F1 > 0.40) per base, 130 escaped runs
(b) test prediction class counts per run: collapsed runs predict (almost) one class
Source: results/runs/*.json -> escaped, escape_step, test.test_prediction_count_class_{0,1}
"""
import collections

import matplotlib.pyplot as plt
import numpy as np

from common import BASE_LABEL, BASE_ORDER, COL_W, GRAY, PALETTE, load_runs, save, style

style()
runs = load_runs()
steps = list(range(200, 2001, 200))

fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.75), gridspec_kw={"width_ratios": [1.25, 1]})

# (a) escape steps ---------------------------------------------------------
ax = axes[0]
base_col = {"xlm15": PALETTE[6], "xlmr": PALETTE[2]}
w = 0.42
for i, b in enumerate(BASE_ORDER):
    cnt = collections.Counter(r["escape_step"] for r in runs if r["base"] == b and r["escaped"])
    vals = [cnt.get(s, 0) for s in steps]
    ax.bar(np.arange(len(steps)) + (i - 0.5) * w, vals, width=w * 0.95, color=base_col[b],
           label=f"{BASE_LABEL[b]} ({sum(vals)} escaped of {sum(1 for r in runs if r['base']==b)})")
    for x, v in zip(np.arange(len(steps)) + (i - 0.5) * w, vals):
        if v:
            ax.text(x, v + 0.8, str(v), ha="center", va="bottom", fontsize=5.5, color=GRAY)
ax.set_xticks(range(len(steps)), [str(s) if s in (200, 600, 1000, 1400, 1800) else "" for s in steps])
ax.set_xlabel("escape step")
ax.set_ylabel("runs")
ax.set_ylim(0, 78)
ax.set_title("(a) When escape happens", loc="left")
ax.legend(frameon=False, fontsize=5.8, loc="upper right", handlelength=1.0)
ax.grid(axis="x", visible=False)

# (b) collapse structure ---------------------------------------------------
ax = axes[1]
xs, ys, cs = [], [], []
for r in runs:
    c0 = r["test"]["test_prediction_count_class_0"]
    c1 = r["test"]["test_prediction_count_class_1"]
    xs.append(c1 / (c0 + c1))
    ys.append(r["test"]["test_macro_f1"])
    cs.append(base_col[r["base"]] if r["escaped"] else PALETTE[7])
xs, ys = np.array(xs), np.array(ys)
ax.scatter(xs, ys, s=9, c=cs, alpha=0.8, linewidths=0.3, edgecolors="white")
ax.axhline(1 / 3, color=GRAY, lw=0.5, ls=":")
ax.axvline(2092 / 4186, color=GRAY, lw=0.5, ls=":")
ax.set_xlabel("share of test predictions = positive")
ax.set_ylabel("test macro-F1")
ax.set_xlim(-0.03, 1.03)
ax.set_ylim(0.28, 0.85)
ax.set_title("(b) Collapse = one-class output", loc="left")
n_col = sum(1 for r in runs if not r["escaped"])
n_one = sum(1 for r in runs if not r["escaped"] and
            (r["test"]["test_prediction_count_class_0"] == 0 or r["test"]["test_prediction_count_class_1"] == 0))
ax.text(0.2, 0.44, f"{n_col} collapsed runs,\n{n_one} predict a\nsingle class", ha="left", va="bottom",
        fontsize=5.8, color=PALETTE[7])
ax.text(0.98, 0.83, "escaped\n(colour = base)", ha="right", va="top", fontsize=5.8, color=GRAY)

fig.tight_layout(w_pad=0.6)
save(fig, "fig_escape.pdf")
