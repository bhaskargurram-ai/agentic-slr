"""Figure 1: PRISMA-style flow diagram aggregated across 5 reviews.

Cleanup:
- Larger figsize (12 x 9) for higher resolution at journal scale
- GT-trials sidebar matched to main flow (same border, padding, font)
- Sidebar vertically aligned to top of the main flow
- Loss-annotation boxes share styling with sidebar
- Anchor coordinates computed once so arrows always reach box edges

Funnel totals (across 5 reviews):
  - Retrieved: 124 + 244 + 2,497 + 370 + 1,107 = 4,342
  - Screening INCLUDE: 47 + 110 + 1,256 + 120 + 278 = 1,811
  - Fulltext-agent INCLUDE: 12 + 56 + 23 + 94 + 72 = 257
  - Final after dedup: 7 + 14 + 23 + 50 + 60 = 154
  - GT in pool: 7 + 7 + 9 + 22 + 11 = 56
  - GT total: 7 + 9 + 9 + 24 + 13 = 62
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 12)
ax.set_ylim(0, 13)
ax.axis("off")

MAIN = "#E8EEF6"   # main flow
GT   = "#FAF1D9"   # GT highlights
LOSS = "#FBE9E7"   # exclusion boxes
SIDE = "#F0F0F0"   # GT sidebar

BOX_KW = dict(boxstyle="round,pad=0.18", linewidth=1.0,
              edgecolor="black", mutation_scale=1.0)


def box(x, y, w, h, text, face=MAIN, fs=10):
    p = FancyBboxPatch((x, y), w, h, facecolor=face, **BOX_KW)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs)


def arrow(x1, y1, x2, y2):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle="->", mutation_scale=14,
                        color="black", linewidth=1.0)
    ax.add_patch(a)


# Main flow column (centered around x = 6.0, width 6.0)
xL, w = 3.0, 6.0
heights = 0.95
gap = 0.55

stages = [
    ("Records identified through PubMed E-utilities search\n"
     "(5 reviews combined: n = 4{,}342)", MAIN),
    ("Abstracts screened by LLM agent\n(gpt-4o-mini)", MAIN),
    ("Records included after abstract screening\nn = 1{,}811", MAIN),
    ("Full-text retrieved (PMC XML preferred)\nn = 1{,}811 (with abstract fallback)", MAIN),
    ("Eligible after full-text agent assessment\nn = 257", MAIN),
    ("Studies included after deduplication\nn = 154 unique primary studies", GT),
    ("Studies passed to extraction (4 LLMs)\n56 of 62 GT trials reached extraction (90.3%)", GT),
]

# Place stages top-down (leave 1.5 unit gap below title at y=12.3)
y_top = 11.4
ys = []
for i, (txt, face) in enumerate(stages):
    y = y_top - i * (heights + gap)
    ys.append(y)
    box(xL, y, w, heights, txt.replace("{,}", ","), face=face)

# Connect with arrows
for i in range(len(stages) - 1):
    arrow(xL + w / 2, ys[i], xL + w / 2, ys[i + 1] + heights)

# Loss annotations (left side), aligned to relevant transitions
loss_x, loss_w = 0.1, 2.7
loss_h = 0.8
loss_items = [
    (1, "Excluded by abstract screener\n2{,}531 records"),
    (3, "Excluded at full-text stage\n1{,}554 records"),
    (5, "Removed at dedup\n(secondary publications): 103 records"),
]
for stage_idx, txt in loss_items:
    target_y = (ys[stage_idx - 1] + ys[stage_idx] + heights) / 2 - loss_h / 2
    box(loss_x, target_y, loss_w, loss_h,
        txt.replace("{,}", ","), face=LOSS, fs=8.5)

# GT sidebar (right side), aligned with header row
side_x = 9.4
side_w = 2.4
hdr_h = 0.6
row_h = 0.45
n_rows = 5
sb_top = ys[0] + heights  # align to top edge of first stage

box(side_x, sb_top - hdr_h, side_w, hdr_h,
    "GT trials per review", face=SIDE, fs=10)
labels = ["r01: 7", "r02: 9", "r03: 9", "r04: 24", "r05: 13"]
for i, t in enumerate(labels):
    y = sb_top - hdr_h - (i + 1) * row_h - 0.08 * i
    box(side_x, y, side_w, row_h, t, face=SIDE, fs=9)

total_y = sb_top - hdr_h - n_rows * row_h - 0.08 * (n_rows - 1) - row_h - 0.10
box(side_x, total_y, side_w, row_h, "Total GT: 62 trials", face=GT, fs=9.5)

ax.text(6.0, 12.55, "Combined PRISMA-style flow across five systematic reviews",
        ha="center", va="center", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig("figure1_prisma.pdf", dpi=300, bbox_inches="tight")
plt.savefig("figure1_prisma.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Figure 1 saved.")
