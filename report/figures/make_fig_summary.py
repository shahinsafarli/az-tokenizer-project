"""Fig. failure-aware summary across training sizes (2 rows x 4 panels).

Row 1: XLM-15 -- (a) escape probability with Wilson 95% CI, (b) conditional validation macro-F1
        with 10,000-resample bootstrap CI, (c) all-seed validation macro-F1 with CI,
        (d) test macro-F1: conditional (solid) and all-seed (hollow)
Row 2: XLM-R -- same, escape panel omitted (5/5 in every cell) and replaced by nothing.
Sources: results/summary.csv (validation), evidence/supplemental/test_tables_received.md T1 (test);
both are exact aggregates of results/runs/*.json.
"""
import matplotlib.pyplot as plt
import numpy as np

from common import (BASE_LABEL, COND_COLOR, COND_LABEL, COND_MARKER, COND_ORDER, GRAY, PAGE_W,
                    load_summary, load_test_cells, save, style)

style()
summ = load_summary()
test = load_test_cells()
sizes = [500, 2000, 10000, 20914]
xpos = {500: 0, 2000: 1, 10000: 2, 20914: 3}


def cell(df, base, cond, n):
    r = df[(df.base == base) & (df.condition == cond) & (df.train_size == n)]
    return r.iloc[0] if len(r) else None


fig, axes = plt.subplots(2, 4, figsize=(PAGE_W, 3.9))
for i, base in enumerate(["xlm15", "xlmr"]):
    for cond in COND_ORDER:
        xs, esc, elo, ehi, cf, clo, chi, af, alo, ahi, tf, tlo, thi, ta = ([] for _ in range(14))
        for n in sizes:
            r = cell(summ, base, cond, n)
            if r is None:
                continue
            t = cell(test, base, cond, n)
            xs.append(xpos[n] + (COND_ORDER.index(cond) - 3) * 0.055)
            esc.append(r.escape_rate); elo.append(r.escape_rate_wilson_ci[0]); ehi.append(r.escape_rate_wilson_ci[1])
            cf.append(r.conditional_macro_f1); clo.append(r.conditional_macro_f1_bootstrap_ci[0]); chi.append(r.conditional_macro_f1_bootstrap_ci[1])
            af.append(r.all_seed_macro_f1); alo.append(r.all_seed_macro_f1_bootstrap_ci[0]); ahi.append(r.all_seed_macro_f1_bootstrap_ci[1])
            tf.append(t.test_cond); tlo.append(t.test_cond_lo); thi.append(t.test_cond_hi); ta.append(t.test_all)
        if not xs:
            continue
        col, mk = COND_COLOR[cond], COND_MARKER[cond]
        kw = dict(color=col, marker=mk, ms=3.2, lw=0.9, mec="white", mew=0.3, label=COND_LABEL[cond], capsize=0)
        xs, esc, cf, af, tf, ta = map(np.array, (xs, esc, cf, af, tf, ta))
        ax = axes[i, 0]
        ax.errorbar(xs, esc, yerr=[esc - np.array(elo), np.array(ehi) - esc], elinewidth=0.5, alpha=0.9, **kw)
        ax = axes[i, 1]
        ax.errorbar(xs, cf, yerr=[cf - np.array(clo), np.array(chi) - cf], elinewidth=0.5, alpha=0.9, **kw)
        ax = axes[i, 2]
        ax.errorbar(xs, af, yerr=[af - np.array(alo), np.array(ahi) - af], elinewidth=0.5, alpha=0.9, **kw)
        ax = axes[i, 3]
        ax.errorbar(xs, tf, yerr=[tf - np.array(tlo), np.array(thi) - tf], elinewidth=0.5, alpha=0.9, **kw)
        ax.plot(xs, ta, color=col, marker=mk, ms=3.2, lw=0.0, mfc="white", mec=col, mew=0.7, alpha=0.9)
    for j, ax in enumerate(axes[i]):
        ax.set_xticks(range(4), ["500", "2k", "10k", "20.9k"])
        ax.set_xlim(-0.5, 3.5 if base == "xlm15" else 1.5)
        ax.grid(axis="x", visible=False)
        if i == 1:
            ax.set_xlabel("Azerbaijani training examples $n$")
    axes[i, 0].set_ylabel(f"{BASE_LABEL[base]}\nescape probability")
    axes[i, 0].set_ylim(-0.05, 1.08)
    for j in (1, 2, 3):
        axes[i, j].set_ylim((0.3, 0.85) if base == "xlm15" else (0.66, 0.86))
    axes[i, 1].set_ylabel("validation macro-F1\n(conditional on escape)")
    axes[i, 2].set_ylabel("validation macro-F1\n(all seeds)")
    axes[i, 3].set_ylabel("test macro-F1\n(filled: conditional; hollow: all seeds)")
for j, t in enumerate(["(a) Escape probability", "(b) Conditional validation F1",
                       "(c) All-seed validation F1", "(d) Test F1 (selected checkpoint)"]):
    axes[0, j].set_title(t, loc="left", fontsize=7)
axes[1, 0].text(0.5, 0.5, "every XLM-R cell\nescaped 5/5", transform=axes[1, 0].transAxes, ha="center", va="center",
                fontsize=7, color=GRAY)
h, l = axes[0, 1].get_legend_handles_labels()
fig.legend(h, l, ncol=7, loc="lower center", bbox_to_anchor=(0.5, -0.01), frameon=False, handlelength=1.4, columnspacing=1.2)
fig.tight_layout(rect=(0, 0.04, 1, 1), h_pad=0.8, w_pad=0.6)
save(fig, "fig_summary.pdf")
