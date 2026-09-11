"""Fig. intrinsic transplant diagnostics (4 panels).

(a) anchor counts by identification mode   <- results/anchors.json
(b) masked-token top-1 accuracy             <- results/top1_accuracy.json
(c) bits per character                       <- results/cross_base_transplant_quality.json
(d) reconstructed/anchor median norm ratio  <- results/embedding_norm_report__{xlm15,xlmr}.json
"""
import matplotlib.pyplot as plt
import numpy as np

from common import (BASE_LABEL, BASE_ORDER, GRAY, PAGE_W, PALETTE, RESULTS, load_json, save, style)

style()
anch = load_json(RESULTS / "anchors.json")["bases"]
top1 = load_json(RESULTS / "top1_accuracy.json")
qual = load_json(RESULTS / "cross_base_transplant_quality.json")["per_base"]
norm = {b: load_json(RESULTS / f"embedding_norm_report__{b}.json") for b in BASE_ORDER}

fig, axes = plt.subplots(1, 4, figsize=(PAGE_W, 2.05), gridspec_kw={"width_ratios": [1.3, 1, 1, 0.9]})
C_BASE, C_TRANS = "#9a9891", PALETTE[1]

# (a) anchors ---------------------------------------------------------------
ax = axes[0]
modes = ["strict", "surface", "functional"]
w = 0.26
for j, mode in enumerate(modes):
    vals = [anch[b]["modes"][mode]["n_anchors"] for b in BASE_ORDER]
    col = [PALETTE[6], PALETTE[3], PALETTE[0]][j]
    bb = ax.bar(np.arange(2) + (j - 1) * w, vals, width=w * 0.92, color=col, label=mode)
    for b_, v in zip(bb, vals):
        ax.text(b_.get_x() + b_.get_width() / 2, v + 150, f"{v:,}", ha="center", va="bottom", fontsize=6)
ax.set_xticks(range(2), [BASE_LABEL[b] for b in BASE_ORDER])
ax.set_ylabel("Donor tokens anchored")
ax.set_ylim(0, 13500)
ax.set_title("(a) Anchor identification", loc="left")
ax.legend(frameon=False, loc="upper left", fontsize=6, handlelength=1.0)
ax.grid(axis="x", visible=False)
ax.text(0.98, 0.97, "vocab 32,770", transform=ax.transAxes, ha="right", va="top", fontsize=6, color=GRAY)

# (b) top-1 -----------------------------------------------------------------
ax = axes[1]
for i, b in enumerate(BASE_ORDER):
    base_acc = top1[b]["base"]["top1_accuracy"] * 100
    tr_acc = top1[b]["transplanted"]["top1_accuracy"] * 100
    ax.bar(i - 0.17, base_acc, width=0.32, color=C_BASE, label="original" if i == 0 else None)
    ax.bar(i + 0.17, tr_acc, width=0.32, color=C_TRANS, label="OMP transplant" if i == 0 else None)
    ax.text(i - 0.17, base_acc + 0.6, f"{top1[b]['base']['n_correct']}/{top1[b]['base']['n_masked_tokens']:,}",
            ha="center", va="bottom", fontsize=5.5, rotation=90 if base_acc < 2 else 0)
    ax.text(i + 0.17, tr_acc + 0.6, f"{top1[b]['transplanted']['n_correct']}/{top1[b]['transplanted']['n_masked_tokens']:,}",
            ha="center", va="bottom", fontsize=5.5, rotation=90 if tr_acc < 5 else 0)
ax.set_xticks(range(2), [BASE_LABEL[b] for b in BASE_ORDER])
ax.set_ylabel("Masked-token top-1 (%)")
ax.set_ylim(0, 52)
ax.set_title("(b) MLM top-1 accuracy", loc="left")
ax.legend(frameon=False, loc="upper left", fontsize=6, handlelength=1.0, bbox_to_anchor=(-0.02, 1.02), ncol=1)
ax.grid(axis="x", visible=False)

# (c) BPC ---------------------------------------------------------------------
ax = axes[2]
for i, b in enumerate(BASE_ORDER):
    bpc_b, bpc_t = qual[b]["C1c_bpc_base"], qual[b]["C1c_bpc_transplanted"]
    ax.bar(i - 0.17, bpc_b, width=0.32, color=C_BASE)
    ax.bar(i + 0.17, bpc_t, width=0.32, color=C_TRANS)
    ax.text(i - 0.17, bpc_b + 0.15, f"{bpc_b:.2f}", ha="center", va="bottom", fontsize=6)
    ax.text(i + 0.17, bpc_t + 0.15, f"{bpc_t:.2f}", ha="center", va="bottom", fontsize=6)
    d = qual[b]["C1c_delta_bpc"]
    ax.text(i, 8.6, f"Δ = {d:+.2f}", ha="center", fontsize=6.5, color=GRAY)
ax.set_xticks(range(2), [BASE_LABEL[b] for b in BASE_ORDER])
ax.set_ylabel("Bits per character")
ax.set_ylim(0, 9.6)
ax.set_title("(c) Masked-LM BPC", loc="left")
ax.grid(axis="x", visible=False)

# (d) norm ratio -------------------------------------------------------------
ax = axes[3]
lo, hi = norm["xlm15"]["healthy_ratio_range"]
ax.axhspan(lo, hi, color=PALETTE[2], alpha=0.18, lw=0)
ax.axhline(1.0, color=GRAY, lw=0.6, ls=":")
for i, b in enumerate(BASE_ORDER):
    r = norm[b]["reconstructed_to_anchor_median_ratio"]
    ok = norm[b]["in_healthy_range"]
    ax.bar(i, r, width=0.5, color=PALETTE[2] if ok else PALETTE[7])
    ax.text(i, r + 0.04, f"{r:.3f}", ha="center", va="bottom", fontsize=6.5)
ax.set_xticks(range(2), [BASE_LABEL[b] for b in BASE_ORDER])
ax.set_ylabel("Reconstructed / anchor\nmedian row norm")
ax.set_ylim(0, 2.4)
ax.set_title("(d) Norm ratio", loc="left")
ax.text(0.03, lo - 0.04, "healthy band 0.85–1.15", ha="left", va="top", fontsize=5.5, color=GRAY,
        transform=ax.get_yaxis_transform())
ax.grid(axis="x", visible=False)

fig.tight_layout(w_pad=0.8)
save(fig, "fig_intrinsic.pdf")
