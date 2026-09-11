"""Fig. forest plot of every XLM-R within-base contrast (n = 500 and n = 2,000).

Validation: conditional difference (comparison - baseline) with 10,000-resample bootstrap CI
            and Holm-adjusted Welch p over the 86-test family  <- results/stats.csv
Test:       paired difference on the same seeds                <- results/runs/*.json (recomputed:
            mean over seeds of test macro-F1 difference; identical to T2/T5 of
            evidence/supplemental/test_tables_received.md because all XLM-R seeds escaped)
"""
import matplotlib.pyplot as plt
import numpy as np

from common import (COL_W, COND_LABEL, GRAY, PALETTE, load_runs, load_stats, save, style)

style()
st = load_stats()
runs = load_runs()


def test_f1(base, cond, n):
    return {r["seed"]: r["test"]["test_macro_f1"] for r in runs
            if r["base"] == base and r["condition"] == cond and r["train_size"] == n}


rows = []
for n in (500, 2000):
    sub = st[(st.base == "xlmr") & (st.train_size == n)].copy()
    for _, r in sub.iterrows():
        a, b = test_f1("xlmr", r.baseline, n), test_f1("xlmr", r.comparison, n)
        dtest = float(np.mean([b[s] - a[s] for s in a]))
        rows.append(dict(n=n, label=f"{COND_LABEL[r.baseline]} → {COND_LABEL[r.comparison]}",
                         d=r.conditional_diff, lo=r.conditional_ci_low, hi=r.conditional_ci_high,
                         holm=r.p_adjusted_holm, surv=bool(r.survives_family_correction), dtest=dtest))
# sort within size by effect
rows = sorted(rows, key=lambda x: (x["n"], x["d"]))

fig, axes = plt.subplots(1, 2, figsize=(COL_W * 2.05, 4.3), sharex=True)
for ax, n in zip(axes, (500, 2000)):
    sub = [r for r in rows if r["n"] == n]
    y = np.arange(len(sub))
    for k, r in enumerate(sub):
        col = PALETTE[0] if r["surv"] else GRAY
        ax.plot([r["lo"], r["hi"]], [k, k], color=col, lw=1.0)
        ax.plot(r["d"], k, marker="o", ms=3.6, color=col, mec="white", mew=0.4)
        ax.plot(r["dtest"], k, marker="D", ms=3.0, color=PALETTE[1], mfc="white", mec=PALETTE[1], mew=0.8)
        ptxt = "<1e-5" if r["holm"] == 0 else (f"{r['holm']:.3g}" if r["holm"] < 1 else "1")
        ax.text(0.135, k, ptxt, va="center", ha="left", fontsize=5.6,
                color=col, fontweight="bold" if r["surv"] else "normal")
    ax.axvline(0, color=GRAY, lw=0.6)
    ax.set_yticks(y, [r["label"] for r in sub], fontsize=6)
    ax.set_ylim(-0.7, len(sub) - 0.3)
    ax.set_xlim(-0.13, 0.17)
    ax.set_xlabel("Δ macro-F1 (comparison − baseline)")
    ax.set_title(f"XLM-R, $n$ = {n:,}", loc="left")
    ax.text(0.135, len(sub) - 0.35, "Holm $p$", ha="left", va="bottom", fontsize=6, color=GRAY, style="italic")
    ax.grid(axis="y", visible=False)
h = [plt.Line2D([], [], color=PALETTE[0], marker="o", lw=1, ms=3.6, mec="white"),
     plt.Line2D([], [], color=GRAY, marker="o", lw=1, ms=3.6, mec="white"),
     plt.Line2D([], [], color=PALETTE[1], marker="D", lw=0, ms=3.0, mfc="white", mew=0.8)]
fig.legend(h, ["validation Δ, bootstrap 95% CI — survives Holm (86-test family)",
               "validation Δ, bootstrap 95% CI — does not survive Holm",
               "test Δ, same seeds (confirmation only)"],
           loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.005), fontsize=6, handlelength=1.8)
fig.tight_layout(rect=(0, 0.05, 1, 1), w_pad=1.2)
save(fig, "fig_forest.pdf")
