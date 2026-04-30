"""Figure 2: v2 extraction accuracy per model per review (4 LLMs x 5 SLRs).

Data source: reviews/PHASE2_FINAL_REPORT.md, Section 2 (V2 post-processed).
"""
import matplotlib.pyplot as plt
import numpy as np

# Real numbers from Phase 2 final report (Section 2)
models = ["GPT-4o-mini", "Llama 3.3 70B", "Qwen 3 235B", "DeepSeek V3"]
reviews = ["r01\n(Epilepsy)", "r02\n(Cardiology)", "r03\n(Oncology)",
           "r04\n(Psychiatry)", "r05\n(Respiratory)"]
acc = np.array([
    [83.1, 79.2, 75.8, 76.9, 64.5],   # gpt-4o-mini
    [83.1, 79.2, 72.7, 77.9, 62.8],   # llama-3.3-70b
    [88.3, 87.0, 78.8, 79.3, 71.1],   # qwen-3-235b
    [84.4, 88.3, 80.8, 81.8, 68.6],   # deepseek-v3
])
means = np.array([75.9, 75.1, 80.9, 80.8])
sds = np.array([6.2, 7.0, 6.2, 6.6])

fig, ax = plt.subplots(figsize=(8.5, 4.6))
x = np.arange(len(reviews))
width = 0.20
colors = ["#5B85AA", "#7DA87B", "#D29F4A", "#B66D6D"]

for i, (m, c) in enumerate(zip(models, colors)):
    ax.bar(x + (i - 1.5) * width, acc[i], width, label=m, color=c, edgecolor="black", linewidth=0.4)

ax.set_xticks(x)
ax.set_xticklabels(reviews, fontsize=9)
ax.set_ylabel("V2 post-processed accuracy (%)", fontsize=10)
ax.set_ylim(50, 95)
ax.axhline(78.2, color="gray", linestyle=":", linewidth=1)
ax.text(4.5, 78.6, "Grand mean 78.2%", color="gray", ha="right", fontsize=8)
ax.legend(loc="lower left", fontsize=8, ncol=4, frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_title(f"Per-model v2 extraction accuracy (means $\\pm$ SD across 5 reviews)",
             fontsize=10)

# Inset for means with error bars
ax2 = fig.add_axes([0.71, 0.55, 0.18, 0.30])
ax2.bar(np.arange(4), means, yerr=sds, color=colors, capsize=3, edgecolor="black", linewidth=0.3)
ax2.set_xticks(np.arange(4))
ax2.set_xticklabels(["GPT", "Lla", "Qwen", "DSv3"], fontsize=7)
ax2.set_ylim(60, 90)
ax2.set_ylabel("Mean (%)", fontsize=7)
ax2.tick_params(axis="y", labelsize=7)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("figure2_model_accuracy.pdf", bbox_inches="tight")
plt.savefig("figure2_model_accuracy.png", bbox_inches="tight", dpi=200)
print("Figure 2 saved.")
