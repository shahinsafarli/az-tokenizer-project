"""Fig. validation macro-F1 trajectories at n = 2,000, all 70 runs.

Source: results/runs/base=*__cond=*__n=2000__seed=*.json -> step_history
(10 evaluation points at steps 200..2000).  Rows = base, columns = condition,
one line per seed.  Collapsed basin (1/3) and escape threshold (0.40) marked.
"""
import matplotlib.pyplot as plt

from common import (BASE_LABEL, BASE_ORDER, COLLAPSE_F1, COND_COLOR, COND_LABEL, COND_ORDER,
                    ESCAPE_THRESHOLD, GRAY, PAGE_W, load_runs, save, style)

style()
runs = [r for r in load_runs() if r["train_size"] == 2000]
assert len(runs) == 70

fig, axes = plt.subplots(2, 7, figsize=(PAGE_W, 2.6), sharex=True, sharey=True)
for i, base in enumerate(BASE_ORDER):
    for j, cond in enumerate(COND_ORDER):
        ax = axes[i, j]
        cell = [r for r in runs if r["base"] == base and r["condition"] == cond]
        assert len(cell) == 5, (base, cond, len(cell))
        n_esc = 0
        for r in sorted(cell, key=lambda r: r["seed"]):
            steps = [h["step"] for h in r["step_history"]]
            f1 = [h["eval_macro_f1"] for h in r["step_history"]]
            esc = r["escaped"]
            n_esc += esc
            ax.plot(steps, f1, color=COND_COLOR[cond] if esc else GRAY, alpha=0.9 if esc else 0.55,
                    lw=1.0 if esc else 0.8, ls="-" if esc else "--")
            ax.plot(r["selected_step"], r["selected_validation_macro_f1"], marker="o", ms=2.2,
                    color=COND_COLOR[cond] if esc else GRAY, mec="white", mew=0.3)
        ax.axhline(COLLAPSE_F1, color=GRAY, lw=0.5, ls=":")
        ax.axhline(ESCAPE_THRESHOLD, color=GRAY, lw=0.5, ls="-.")
        ax.set_ylim(0.28, 0.9)
        ax.set_xlim(150, 2050)
        ax.set_xticks([200, 1000, 2000])
        ax.set_xticklabels(["200", "1k", "2k"])
        ax.set_yticks([0.333, 0.4, 0.5, 0.6, 0.7, 0.8])
        ax.set_yticklabels(["⅓", ".40", ".5", ".6", ".7", ".8"])
        ax.tick_params(length=2, pad=1.5)
        ax.grid(axis="x", visible=False)
        if i == 0:
            ax.set_title(COND_LABEL[cond], fontsize=7.5, pad=3, color=COND_COLOR[cond])
        ax.text(0.97, 0.05, f"{n_esc}/5", transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color=GRAY)
        if j == 0:
            ax.set_ylabel(f"{BASE_LABEL[base]}\nvalidation macro-F1", fontsize=7)
        if i == 1:
            ax.set_xlabel("optimizer step", fontsize=7)
fig.tight_layout(h_pad=0.4, w_pad=0.25)
save(fig, "fig_trajectories.pdf")
