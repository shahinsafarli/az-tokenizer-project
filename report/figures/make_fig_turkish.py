"""Fig. Turkish source stage (2 panels).

(a) Turkish-stage validation macro-F1 (3-class) of every Turkish-bearing run, by base and condition,
    with the degeneracy threshold 0.40                       <- results/aggregate.csv
(b) downstream Azerbaijani selected validation macro-F1 vs Turkish-stage macro-F1 (60 runs);
    collapsed downstream runs marked                          <- results/aggregate.csv
"""
import matplotlib.pyplot as plt
import numpy as np

from common import (BASE_LABEL, COL_W, COLLAPSE_F1, COND_COLOR, COND_LABEL, COND_MARKER, GRAY, PALETTE,
                    load_aggregate, save, style)

style()
agg = load_aggregate()
tr = agg[agg.turkish != "none"].copy()
assert len(tr) == 60
tr["deg"] = tr.tr_stage_degenerate.astype(str).str.lower() == "true"
conds = ["turk", "her_ikisi", "turk_qarisiq"]

fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.9), gridspec_kw={"width_ratios": [1.15, 1]})

# (a) strip plot -------------------------------------------------------------
ax = axes[0]
rng = np.random.default_rng(0)
x = 0
ticks, labels = [], []
for b in ("xlm15", "xlmr"):
    for c in conds:
        s = tr[(tr.base == b) & (tr.condition == c)]
        assert len(s) == 10
        jit = rng.uniform(-0.18, 0.18, len(s))
        ax.scatter(x + jit, s.tr_stage_macro_f1, s=11, color=COND_COLOR[c], marker=COND_MARKER[c],
                   linewidths=0.3, edgecolors="white", alpha=0.9)
        n_deg = int(s.deg.sum())
        ax.text(x, 0.80, f"{n_deg}/10", ha="center", va="bottom", fontsize=5.8, color=PALETTE[7] if n_deg else GRAY)
        ticks.append(x); labels.append(COND_LABEL[c].replace("Shuf. TR", "Shuf.").replace("OMP+TR", "OMP\n+TR"))
        x += 1
    x += 0.6
ax.axhline(0.40, color=PALETTE[7], lw=0.6, ls="-.")
ax.text(ticks[-1] + 0.45, 0.405, "degenerate\n< 0.40", ha="right", va="bottom", fontsize=5.5, color=PALETTE[7])
ax.set_xticks(ticks, labels, fontsize=6)
ax.set_ylabel("Turkish-stage macro-F1 (3 classes)")
ax.set_ylim(0.1, 0.95)
ax.text(1, 0.88, BASE_LABEL["xlm15"], ha="center", va="bottom", fontsize=6.5, color=GRAY)
ax.text(4.6, 0.88, BASE_LABEL["xlmr"], ha="center", va="bottom", fontsize=6.5, color=GRAY)
ax.set_title("(a) Source-stage quality", loc="left")
ax.grid(axis="x", visible=False)

# (b) downstream vs source ----------------------------------------------------
ax = axes[1]
for b, mk in (("xlm15", "o"), ("xlmr", "s")):
    s = tr[tr.base == b]
    esc = s[s.escaped]
    col = s[~s.escaped]
    ax.scatter(esc.tr_stage_macro_f1, esc.selected_validation_macro_f1, s=11, marker=mk,
               color=[COND_COLOR[c] for c in esc.condition], linewidths=0.3, edgecolors="white", alpha=0.9)
    ax.scatter(col.tr_stage_macro_f1, col.selected_validation_macro_f1, s=14, marker="x",
               color=[COND_COLOR[c] for c in col.condition], linewidths=0.7)
ax.axvline(0.40, color=PALETTE[7], lw=0.6, ls="-.")
ax.axhline(COLLAPSE_F1, color=GRAY, lw=0.5, ls=":")
ax.set_xlabel("Turkish-stage macro-F1")
ax.set_ylabel("AZ validation macro-F1\n(selected checkpoint)")
ax.set_xlim(0.1, 0.9)
ax.set_ylim(0.28, 0.9)
ax.set_title("(b) Source → target", loc="left")
ax.text(0.98, 0.02, "○ XLM-15   □ XLM-R\n× collapsed downstream", transform=ax.transAxes, ha="right", va="bottom",
        fontsize=5.5, color=GRAY)

fig.tight_layout(w_pad=0.7)
save(fig, "fig_turkish.pdf")
