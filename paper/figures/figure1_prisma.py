"""Figure 1: PRISMA-style flow diagram aggregated across 5 reviews.

Data source: per-review PIPELINE_REPORT.md and PHASE2_FINAL_REPORT.md.

Funnel totals (across 5 reviews):
  - Retrieved (deduped): 124 + 244 + 2,497 + 370 + 1,107 = 4,342
  - Screening INCLUDE: 47 + 110 + 1,256 + 120 + 278 = 1,811 (LLM-screened)
  - Fulltext-agent INCLUDE: 12 + 56 + 23 + 94 + 72 = 257
  - Final after dedup: 7 + 14 + 23 + 50 + 60 = 154
  - Ground-truth in pool: 7 + 7 + 9 + 22 + 11 = 56
  - Ground-truth total: 7 + 9 + 9 + 24 + 13 = 62
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import FancyArrowPatch

fig, ax = plt.subplots(figsize=(7.8, 9.0))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis("off")

def box(x, y, w, h, text, color="#E8EEF6"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                       linewidth=1.0, edgecolor="black", facecolor=color)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)

def arrow(x1, y1, x2, y2):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle="->", mutation_scale=12, color="black", linewidth=1.0)
    ax.add_patch(a)

# Main funnel (left column)
box(2.0, 10.6, 6.0, 0.9, "Records identified through PubMed E-utilities search\n(5 reviews combined: n = 4,342)",
    color="#E8EEF6")
arrow(5.0, 10.6, 5.0, 10.0)
box(2.0, 9.1,  6.0, 0.9, "Abstracts screened by LLM agent\n(gpt-4o-mini, n = 4,342)", color="#E8EEF6")
arrow(5.0, 9.1, 5.0, 8.5)
box(2.0, 7.6,  6.0, 0.9, "Records included after abstract screening\nn = 1,811 across 5 reviews",
    color="#E8EEF6")
arrow(5.0, 7.6, 5.0, 7.0)
box(2.0, 6.1,  6.0, 0.9, "Full-text retrieved (PMC XML preferred)\nn = 1,811 with abstract+ fallback",
    color="#E8EEF6")
arrow(5.0, 6.1, 5.0, 5.5)
box(2.0, 4.6,  6.0, 0.9, "Eligible after full-text agent assessment\nn = 257 across 5 reviews",
    color="#E8EEF6")
arrow(5.0, 4.6, 5.0, 4.0)
box(2.0, 3.1,  6.0, 0.9, "Studies included after deduplication\nn = 154 unique primary studies",
    color="#FAF1D9")
arrow(5.0, 3.1, 5.0, 2.5)
box(2.0, 1.6,  6.0, 0.9, "Studies passed to extraction (4 LLMs)\n56 / 62 GT trials reached extraction (90.3%)",
    color="#D9EAD3")

# Right side: ground-truth tally
box(8.5, 10.6, 1.4, 0.9, "GT trials\nper review", color="#F0F0F0")
labels = ["r01: 7", "r02: 9", "r03: 9", "r04: 24", "r05: 13"]
for i, t in enumerate(labels):
    box(8.5, 10.0 - i * 0.7, 1.4, 0.55, t, color="#F0F0F0")
box(8.5, 5.9, 1.4, 0.9, "Total GT\n62 trials", color="#FAF1D9")

# Loss annotations
box(0.05, 9.55, 1.85, 0.9, "Excluded by abstract\nscreener:\n2,531 records",
    color="#FBE9E7")
box(0.05, 4.95, 1.85, 0.9, "Excluded at full-text\nstage:\n1,554 records",
    color="#FBE9E7")
box(0.05, 1.95, 1.85, 0.9, "Removed at dedup\n(secondary publications):\n103 records",
    color="#FBE9E7")

# Title
ax.text(5.0, 11.7, "Combined PRISMA-style flow across five systematic reviews",
        ha="center", va="center", fontsize=11, fontweight="bold")

plt.tight_layout()
plt.savefig("figure1_prisma.pdf", bbox_inches="tight")
plt.savefig("figure1_prisma.png", bbox_inches="tight", dpi=200)
print("Figure 1 saved.")
