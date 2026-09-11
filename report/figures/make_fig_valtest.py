"""Fig. validation vs test (3 panels).

(a) selected-checkpoint validation macro-F1 vs test macro-F1, all 164 runs   <- results/aggregate.csv
(b) histogram of the matched gap test - validation                            <- results/aggregate.csv
(c) contrast-level: paired validation Δ vs paired test Δ, 38 contrasts        <- T2 of
    evidence/supplemental/test_tables_received.md (n shared >= 1)
"""
import matplotlib.pyplot as plt
import numpy as np

from common import (BASE_LABEL, GRAY, PAGE_W, PALETTE, load_aggregate, parse_test_tables, save, style)

style()
agg = load_aggregate()
t2 = parse_test_tables()["T2"]
base_col = {"xlm15": PALETTE[6], "xlmr": PALETTE[2]}

fig, axes = plt.subplots(1, 3, figsize=(PAGE_W, 2.15), gridspec_kw={"width_ratios": [1, 1, 1]})

# (a) --------------------------------------------------------------------------
ax = axes[0]
for b in ("xlm15", "xlmr"):
    s = agg[agg.base == b]
    esc = s[s.escaped]
    col = s[~s.escaped]
    ax.scatter(esc.selected_validation_macro_f1, esc.test_macro_f1, s=9, color=base_col[b], alpha=0.8,
               linewidths=0.3, edgecolors="white", label=f"{BASE_LABEL[b]} escaped ({len(esc)})")
    ax.scatter(col.selected_validation_macro_f1, col.test_macro_f1, s=9, color=base_col[b], alpha=0.8,
               marker="x", linewidths=0.7, label=f"{BASE_LABEL[b]} collapsed ({len(col)})" if len(col) else None)
lim = (0.3, 0.86)
ax.plot(lim, lim, color=GRAY, lw=0.6, ls="--")
ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("validation macro-F1 (selected checkpoint)")
ax.set_ylabel("test macro-F1 (same checkpoint)")
ax.set_title("(a) All 164 runs", loc="left")
ax.legend(frameon=False, fontsize=5.8, loc="upper left", handlelength=1.0, borderaxespad=0.2)
ax.set_aspect("equal")

# (b) --------------------------------------------------------------------------
ax = axes[1]
bins = np.arange(-0.040, 0.0125, 0.0025)
for b in ("xlm15", "xlmr"):
    s = agg[agg.base == b].delta_test_minus_validation_matched
    ax.hist(s, bins=bins, color=base_col[b], alpha=0.75, label=f"{BASE_LABEL[b]} (mean {s.mean():+.4f})",
            edgecolor="white", linewidth=0.3)
d = agg.delta_test_minus_validation_matched
ax.axvline(d.mean(), color=GRAY, lw=0.8, ls="--")
ax.text(d.mean() - 0.0008, ax.get_ylim()[1] * 0.97, f"all: mean {d.mean():+.4f}\nmedian {d.median():+.4f}\n{(d<0).sum()}/164 negative",
        ha="right", va="top", fontsize=6, color=GRAY)
ax.set_xlabel("Δ = test − validation (matched weights)")
ax.set_ylabel("runs")
ax.set_title("(b) Generalisation gap", loc="left")
ax.legend(frameon=False, fontsize=5.8, loc="upper left", handlelength=1.0)

# (c) --------------------------------------------------------------------------
ax = axes[2]
dv, dt, cols = [], [], []
for _, r in t2.iterrows():
    if r["Δ val (paired)"] == "n/a":
        continue
    dv.append(float(r["Δ val (paired)"])); dt.append(float(r["Δ test (paired)"]))
    cols.append(base_col[r["Base"]])
dv, dt = np.array(dv), np.array(dt)
ax.scatter(dv, dt, s=11, c=cols, alpha=0.85, linewidths=0.3, edgecolors="white")
lim = (-0.13, 0.23)
ax.plot(lim, lim, color=GRAY, lw=0.6, ls="--")
ax.axhline(0, color=GRAY, lw=0.4); ax.axvline(0, color=GRAY, lw=0.4)
r = np.corrcoef(dv, dt)[0, 1]
agree = int(np.sum(np.sign(dv) == np.sign(dt)))
ax.text(0.03, 0.97, f"{len(dv)} paired contrasts\nsign agrees {agree}/{len(dv)}\nPearson r = {r:.4f}",
        transform=ax.transAxes, ha="left", va="top", fontsize=6, color=GRAY)
ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("Δ validation (paired, shared seeds)")
ax.set_ylabel("Δ test (same seeds)")
ax.set_title("(c) Contrast-level agreement", loc="left")
ax.set_aspect("equal")

fig.tight_layout(w_pad=0.8)
save(fig, "fig_valtest.pdf")
