"""Fig. the exact sign-flip floor with five seeds, illustrated on one survivor contrast.

Contrast: XLM-R, n = 2,000, Direct -> OMP.  For each of the 2^5 = 32 sign assignments the mean
paired difference is recomputed; the observed statistic is the most extreme, so the two-sided
exact p is 2/32 = 0.0625.  Recomputes the value reported in T6 of
evidence/supplemental/test_tables_received.md from results/runs/*.json.
"""
import itertools

import matplotlib.pyplot as plt
import numpy as np

from common import COL_W, GRAY, PALETTE, load_runs, save, style

style()
runs = load_runs()


def scores(cond, split):
    out = {}
    for r in runs:
        if r["base"] == "xlmr" and r["train_size"] == 2000 and r["condition"] == cond:
            out[r["seed"]] = r["selected_validation_macro_f1"] if split == "val" else r["test"]["test_macro_f1"]
    return out


fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.75), sharey=True)
for ax, split, title in zip(axes, ("val", "test"), ("(a) validation", "(b) test")):
    a, b = scores("baza", split), scores("tokenizator", split)
    d = np.array([b[s] - a[s] for s in sorted(a)])
    obs = d.mean()
    null = np.array([np.mean(d * np.array(signs)) for signs in itertools.product([1, -1], repeat=5)])
    p = np.mean(np.abs(null) >= abs(obs) - 1e-12)
    ax.hist(null, bins=24, color="#bcbab3", edgecolor="white", linewidth=0.3)
    ax.axvline(obs, color=PALETTE[1], lw=1.2)
    ax.axvline(-obs, color=PALETTE[1], lw=1.2, ls=":")
    ax.text(0.03, 0.95, f"observed Δ = {obs:+.4f}\nexact p = {int(round(p*32))}/32 = {p:.4f}\nseed Δ: " +
            ", ".join(f"{v:+.3f}" for v in d), transform=ax.transAxes, ha="left", va="top", fontsize=5.6, color=GRAY)
    ax.set_title(title, loc="left")
    ax.set_xlabel("mean paired Δ under sign flips")
    ax.set_xlim(-0.085, 0.085)
axes[0].set_ylabel("assignments (of 32)")
axes[0].set_ylim(0, 11)
fig.suptitle("XLM-R, $n$ = 2,000, Direct → OMP", fontsize=7, y=1.02)
fig.tight_layout(w_pad=0.6)
save(fig, "fig_signflip.pdf")
