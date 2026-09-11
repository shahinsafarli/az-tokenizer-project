"""Fig. tokenizer diagnostics (3 panels).

(a) corpus fertility of Azerbaijani per tokenizer      <- results/overlap_control.json
(b) alphabetic token-type overlap AZ vs TR/EN/FI/RU     <- results/overlap_control.json
(c) truncation rate at max_length 128 / 256              <- results/truncation.json
"""
import matplotlib.pyplot as plt
import numpy as np

from common import (GRAY, PAGE_W, PALETTE, RESULTS, load_json, save, style)

style()
ov = load_json(RESULTS / "overlap_control.json")
tr = load_json(RESULTS / "truncation.json")

MODEL_LABEL = {
    "FacebookAI/xlm-mlm-tlm-xnli15-1024": "XLM-15\n(original)",
    "xlm-roberta-base": "XLM-R\n(original)",
    "HPLT/hplt_bert_base_az": "AZ donor\n(HPLT)",
}
models = ov["models"]
names = [MODEL_LABEL[m["model"]] for m in models]

fig, axes = plt.subplots(1, 3, figsize=(PAGE_W, 2.25), gridspec_kw={"width_ratios": [1, 1.9, 1.2]})

# (a) fertility ------------------------------------------------------------
ax = axes[0]
fert = [m["az_fertility"] for m in models]
bars = ax.bar(range(3), fert, color=[PALETTE[0], PALETTE[2], PALETTE[1]], width=0.6)
for b, v in zip(bars, fert):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.05, f"{v:.2f}", ha="center", va="bottom", fontsize=7)
ax.set_xticks(range(3), names)
ax.set_ylabel("Azerbaijani fertility (tokens / word)")
ax.set_ylim(0, 3.8)
ax.set_title("(a) Segmentation cost", loc="left")
ax.grid(axis="x", visible=False)

# (b) overlap --------------------------------------------------------------
ax = axes[1]
langs = ["tr", "en", "fi", "ru"]
lang_label = {"tr": "Turkish", "en": "English", "fi": "Finnish", "ru": "Russian"}
lang_color = {"tr": PALETTE[0], "en": "#9a9891", "fi": "#9a9891", "ru": PALETTE[7]}
w = 0.19
x = np.arange(3)
for j, lg in enumerate(langs):
    vals = [m["overlaps"][lg]["alpha"]["a_covered_pct"] for m in models]
    bb = ax.bar(x + (j - 1.5) * w, vals, width=w * 0.92, color=lang_color[lg],
                label=lang_label[lg], edgecolor="white", linewidth=0.4)
    for b, v in zip(bb, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.0f}", ha="center", va="bottom", fontsize=6)
for i, m in enumerate(models):
    rs = m["relatedness_signal"]
    ax.hlines(rs["latin_baseline_pct"], x[i] - 2 * w, x[i] + 2 * w, color=GRAY, linestyle="--", linewidth=0.8)
    ax.text(x[i] - 1.5 * w, rs["tr_alpha_pct"] + 7, "lift\n+%.1f pt" % rs["relatedness_lift_points"],
            ha="center", va="bottom", fontsize=6, color=PALETTE[0])
ax.set_xticks(x, names)
ax.set_ylabel("AZ alphabetic types covered (%)")
ax.set_ylim(0, 100)
ax.set_title("(b) Vocabulary overlap with Azerbaijani", loc="left", pad=14)
ax.grid(axis="x", visible=False)
h, l = ax.get_legend_handles_labels()
h.append(plt.Line2D([], [], color=GRAY, linestyle="--", linewidth=0.8))
l.append("Latin baseline (EN, FI mean)")
ax.legend(h, l, ncol=5, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False, columnspacing=0.7, handlelength=1.0, borderaxespad=0.0)

# (c) truncation -------------------------------------------------------------
ax = axes[2]
setups = ["base_original_xlm15", "contrast_original_xlmr", "donor_transplanted"]
setup_label = ["XLM-15\n(original)", "XLM-R\n(original)", "AZ donor\n(HPLT)"]
for j, L in enumerate(["128", "256"]):
    vals = [tr["by_max_length"][L]["setups"][s]["truncation_rate_pct"] for s in setups]
    bb = ax.bar(np.arange(3) + (j - 0.5) * 0.32, vals, width=0.3, color=[PALETTE[3], PALETTE[6]][j],
                label=f"max length {L}")
    for b, v in zip(bb, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", va="bottom", fontsize=6)
ax.set_xticks(range(3), setup_label)
ax.set_ylabel("Examples truncated (%)")
ax.set_title("(c) Truncation, 27,914 examples", loc="left")
ax.legend(frameon=False, loc="upper right")
ax.grid(axis="x", visible=False)

fig.tight_layout(w_pad=1.0)
save(fig, "fig_tokenizer.pdf")
