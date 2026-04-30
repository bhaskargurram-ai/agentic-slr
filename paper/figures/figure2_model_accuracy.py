"""Figure 2: v2 extraction accuracy per model per review (4 LLMs x 5 SLRs).

Two-panel layout: main bar chart (75% width) with legend in upper-left,
mean+/-SD inset as a separate right panel (25% width).

Data source: reviews/PHASE2_FINAL_REPORT.md, Section 2 (V2 post-processed).
"""
import matplotlib.pyplot as plt
import numpy as np

reviews = ["r01\n(Epilepsy)", "r02\n(Cardiology)", "r03\n(Oncology)",
           "r04\n(Psychiatry)", "r05\n(Respiratory)"]
models = ["GPT-4o-mini", "Llama 3.3 70B", "Qwen 3 235B", "DeepSeek V3"]
data = {
    "GPT-4o-mini":   [83.1, 79.2, 75.8, 76.9, 64.5],
    "Llama 3.3 70B": [83.1, 79.2, 72.7, 77.9, 62.8],
    "Qwen 3 235B":   [88.3, 87.0, 78.8, 79.3, 71.1],
    "DeepSeek V3":   [84.4, 88.3, 80.8, 81.8, 68.6],
}
colors = {"GPT-4o-mini": "#4C72B0", "Llama 3.3 70B": "#55A868",
          "Qwen 3 235B": "#C44E52", "DeepSeek V3": "#8172B2"}
short = {"GPT-4o-mini": "GPT", "Llama 3.3 70B": "Lla",
         "Qwen 3 235B": "Qwen", "DeepSeek V3": "DSv3"}

fig, (ax_main, ax_inset) = plt.subplots(
    1, 2, figsize=(14, 6),
    gridspec_kw={"width_ratios": [3, 1]},
)

x = np.arange(len(reviews))
width = 0.20
for i, m in enumerate(models):
    ax_main.bar(x + i * width, data[m], width, label=m,
                color=colors[m], edgecolor="black", linewidth=0.5)

ax_main.axhline(y=78.2, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
ax_main.text(4.32, 79.0, "Grand mean 78.2%",
             fontsize=9, color="gray", ha="right", style="italic")

ax_main.set_xticks(x + 1.5 * width)
ax_main.set_xticklabels(reviews, fontsize=10)
ax_main.set_ylabel("V2 post-processed accuracy (%)", fontsize=11)
ax_main.set_ylim(50, 95)
ax_main.set_xlim(-0.4, len(reviews) - 1 + 4 * width + 0.1)
ax_main.legend(loc="upper left", fontsize=9, frameon=True, framealpha=0.95,
               ncol=2)
ax_main.grid(axis="y", alpha=0.3, linestyle=":")
ax_main.set_axisbelow(True)
ax_main.spines["top"].set_visible(False)
ax_main.spines["right"].set_visible(False)
ax_main.set_title("(a) Per-model accuracy by review", fontsize=11)

means = [np.mean(data[m]) for m in models]
sds   = [np.std(data[m], ddof=1) for m in models]
xs = np.arange(len(models))
bars = ax_inset.bar(xs, means, yerr=sds, color=[colors[m] for m in models],
                    capsize=5, edgecolor="black", linewidth=0.5,
                    error_kw={"elinewidth": 1.2})
ax_inset.set_xticks(xs)
ax_inset.set_xticklabels([short[m] for m in models], fontsize=10)
ax_inset.set_ylabel("Mean (%)", fontsize=10)
ax_inset.set_ylim(60, 90)
ax_inset.set_title("(b) Mean $\\pm$ SD across reviews", fontsize=11)
ax_inset.grid(axis="y", alpha=0.3, linestyle=":")
ax_inset.set_axisbelow(True)
ax_inset.spines["top"].set_visible(False)
ax_inset.spines["right"].set_visible(False)

for xi, mn in zip(xs, means):
    ax_inset.text(xi, mn + 0.4, f"{mn:.1f}", ha="center", va="bottom", fontsize=8)

plt.tight_layout()
plt.savefig("figure2_model_accuracy.pdf", dpi=300, bbox_inches="tight")
plt.savefig("figure2_model_accuracy.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Figure 2 saved.")
