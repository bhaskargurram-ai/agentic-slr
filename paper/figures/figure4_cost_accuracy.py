"""Figure 4: Cost-vs-accuracy frontier (4 models, total Phase 2).

Layout fixes:
- Y-axis bounds 65-92 so error bars are fully inside the plot area
- Annotations placed with explicit offset arrows so labels don't overlap markers
- Log x-axis with major and minor tick formatters

Data source: reviews/PHASE2_FINAL_REPORT.md, Section 6.
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator, FuncFormatter

costs = {"GPT-4o-mini": 0.1442, "Llama 3.3 70B": 0.8530,
         "Qwen 3 235B": 0.2144, "DeepSeek V3": 1.1547}
means = {"GPT-4o-mini": 75.9, "Llama 3.3 70B": 75.1,
         "Qwen 3 235B": 80.9, "DeepSeek V3": 80.8}
sds   = {"GPT-4o-mini": 6.2, "Llama 3.3 70B": 7.0,
         "Qwen 3 235B": 6.2, "DeepSeek V3": 6.6}
colors = {"GPT-4o-mini": "#4C72B0", "Llama 3.3 70B": "#55A868",
          "Qwen 3 235B": "#C44E52", "DeepSeek V3": "#8172B2"}

fig, ax = plt.subplots(figsize=(9, 6))

for m in costs:
    ax.errorbar(costs[m], means[m], yerr=sds[m], fmt="o", markersize=14,
                color=colors[m], capsize=6, capthick=1.5, elinewidth=1.5,
                markeredgecolor="black", markeredgewidth=1.0,
                label=m, zorder=3)

label_offsets = {
    "GPT-4o-mini":   (16,  18),
    "Qwen 3 235B":   (16, -22),
    "Llama 3.3 70B": (16,  18),
    "DeepSeek V3":   (-12, 18),
}
ha_for = {"GPT-4o-mini": "left", "Qwen 3 235B": "left",
          "Llama 3.3 70B": "left", "DeepSeek V3": "right"}

for m in costs:
    dx, dy = label_offsets[m]
    ax.annotate(m, xy=(costs[m], means[m]),
                xytext=(dx, dy), textcoords="offset points",
                ha=ha_for[m], fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color="gray",
                                lw=0.6, alpha=0.7))

ax.set_xscale("log")
ax.set_xlim(0.08, 1.8)
ax.set_ylim(65, 92)
ax.set_xlabel("Total Phase 2 extraction cost (USD)", fontsize=11)
ax.set_ylabel("Mean v2 accuracy across 5 reviews (%)", fontsize=11)
ax.set_title("Cost-quality frontier: open MoE models dominate",
             fontsize=12)

ax.xaxis.set_major_locator(LogLocator(base=10, numticks=5))
ax.xaxis.set_minor_locator(LogLocator(base=10,
                                      subs=(0.2, 0.3, 0.5, 0.7),
                                      numticks=12))
fmt = FuncFormatter(lambda x, _: f"{x:.2f}")
ax.xaxis.set_major_formatter(fmt)
ax.xaxis.set_minor_formatter(fmt)
ax.tick_params(axis="x", which="major", labelsize=9, length=6)
ax.tick_params(axis="x", which="minor", labelsize=8, length=3)

ax.grid(True, which="major", axis="both", alpha=0.4, linestyle=":")
ax.grid(True, which="minor", axis="x", alpha=0.2, linestyle=":")
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.text(0.10, 90.5, "cheaper $\\rightarrow$", fontsize=9, color="gray",
        style="italic")
ax.text(1.55, 90.5, "$\\leftarrow$ more expensive", fontsize=9, color="gray",
        style="italic", ha="right")

plt.tight_layout()
plt.savefig("figure4_cost_accuracy.pdf", dpi=300, bbox_inches="tight")
plt.savefig("figure4_cost_accuracy.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Figure 4 saved.")
