"""Figure 4: Cost-vs-accuracy frontier (4 models, total Phase 2).

Data source: reviews/PHASE2_FINAL_REPORT.md, Section 6.
"""
import matplotlib.pyplot as plt

models = ["GPT-4o-mini", "Llama 3.3 70B", "Qwen 3 235B", "DeepSeek V3"]
cost = [0.1442, 0.8530, 0.2144, 1.1547]   # USD across all 5 reviews
acc  = [75.9, 75.1, 80.9, 80.8]            # mean v2 (%)
sd   = [6.2, 7.0, 6.2, 6.6]                # SD across 5 reviews
colors = ["#5B85AA", "#7DA87B", "#D29F4A", "#B66D6D"]

fig, ax = plt.subplots(figsize=(6.4, 4.6))
for x, y, e, n, c in zip(cost, acc, sd, models, colors):
    ax.errorbar(x, y, yerr=e, fmt="o", color=c, ecolor=c, capsize=4,
                markersize=11, markeredgecolor="black", markeredgewidth=0.6,
                label=n)
    ax.annotate(n, (x, y), xytext=(8, -2), textcoords="offset points",
                fontsize=9)

ax.set_xlabel("Total Phase 2 extraction cost (USD)", fontsize=10)
ax.set_ylabel("Mean v2 accuracy across 5 reviews (%)", fontsize=10)
ax.set_xscale("log")
ax.set_xlim(0.08, 2.0)
ax.set_ylim(70, 88)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linestyle=":", alpha=0.4)
ax.set_title("Cost-quality frontier: open MoE models dominate", fontsize=10)

plt.tight_layout()
plt.savefig("figure4_cost_accuracy.pdf", bbox_inches="tight")
plt.savefig("figure4_cost_accuracy.png", bbox_inches="tight", dpi=200)
print("Figure 4 saved.")
