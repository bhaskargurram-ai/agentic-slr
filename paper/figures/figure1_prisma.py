"""Figure 1: PRISMA-style flow aggregated across 5 reviews.

Layout: 3 columns (left = exclusions, middle = main flow, right = GT tally).
- All boxes use the same FancyBboxPatch styling.
- Vertical spacing is gap-based, never edge-touching.
- Sidebar rows have explicit gaps between them.
- Connector arrows are drawn only between main-flow boxes (centred column).
- Side-arrow stubs link main-flow transitions to the corresponding
  exclusion box on the left.

Funnel totals (across 5 reviews):
  Retrieved:                4,342
  Screening INCLUDE:        1,811
  Fulltext-agent INCLUDE:     257
  Final after dedup:          154
  GT in pool / GT total:      56 / 62
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ----- canvas ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 11))
ax.set_xlim(0, 13)
ax.set_ylim(0, 14.5)
ax.axis("off")

MAIN = "#E8EEF6"
GT   = "#FAF1D9"
LOSS = "#FBE9E7"
SIDE = "#F0F0F0"

BOX_KW = dict(boxstyle="round,pad=0.20", linewidth=1.0, edgecolor="black")


def box(x, y, w, h, text, face=MAIN, fs=10):
    """Draw a labelled rounded-rectangle box with (x, y) at lower-left."""
    p = FancyBboxPatch((x, y), w, h, facecolor=face, **BOX_KW)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def varrow(x, y_top, y_bot):
    a = FancyArrowPatch((x, y_top), (x, y_bot),
                        arrowstyle="->", mutation_scale=14,
                        color="black", linewidth=1.0)
    ax.add_patch(a)


def harrow(x_from, y, x_to):
    a = FancyArrowPatch((x_from, y), (x_to, y),
                        arrowstyle="->", mutation_scale=12,
                        color="black", linewidth=1.0)
    ax.add_patch(a)


# ----- main flow column ------------------------------------------------------
# Geometry: column centred at x=6.5, width 5.0, boxes (1.0 high) with 0.7 gaps.
MAIN_X, MAIN_W = 4.0, 5.0
MAIN_CENTRE = MAIN_X + MAIN_W / 2  # 6.5
H = 1.0
GAP = 0.75

stages = [
    ("Records identified through PubMed E-utilities search\n"
     "(5 reviews combined: n = 4,342)", MAIN),
    ("Abstracts screened by LLM agent\n(gpt-4o-mini)", MAIN),
    ("Records included after abstract screening\nn = 1,811", MAIN),
    ("Full-text retrieved (PMC XML preferred)\nn = 1,811 (with abstract fallback)", MAIN),
    ("Eligible after full-text agent assessment\nn = 257", MAIN),
    ("Studies included after deduplication\nn = 154 unique primary studies", GT),
    ("Studies passed to extraction (4 LLMs)\n"
     "56 of 62 GT trials reached extraction (90.3%)", GT),
]

y_top = 13.0
ys = []
for i, (txt, face) in enumerate(stages):
    y = y_top - i * (H + GAP)
    ys.append(y)
    box(MAIN_X, y, MAIN_W, H, txt, face=face)

# vertical arrows between stages (in the gap, with margin)
for i in range(len(stages) - 1):
    varrow(MAIN_CENTRE, ys[i], ys[i + 1] + H)

# ----- left column: exclusions ----------------------------------------------
# 0.5-wide gutter then 2.7-wide boxes; right edge stops well before MAIN_X.
LOSS_X, LOSS_W, LOSS_H = 0.4, 2.9, 0.85
loss_items = [
    (1, "Excluded by abstract screener:\n2,531 records"),
    (3, "Excluded at full-text stage:\n1,554 records"),
    (5, "Removed at dedup\n(secondary publications): 103 records"),
]
for stage_idx, txt in loss_items:
    target_y_centre = (ys[stage_idx - 1] + ys[stage_idx] + H) / 2
    by = target_y_centre - LOSS_H / 2
    box(LOSS_X, by, LOSS_W, LOSS_H, txt, face=LOSS, fs=8.5)
    # short connector from the box to the main column arrow
    harrow(LOSS_X + LOSS_W, target_y_centre, MAIN_X - 0.05)

# ----- right column: GT tally sidebar ---------------------------------------
SIDE_X, SIDE_W = 10.2, 2.5
HDR_H = 0.55
ROW_H = 0.50
ROW_GAP = 0.10

# header aligned with TOP edge of the first main box
sb_top = ys[0] + H
hdr_y = sb_top - HDR_H
box(SIDE_X, hdr_y, SIDE_W, HDR_H, "GT trials per review",
    face=SIDE, fs=10)

labels = ["r01: 7", "r02: 9", "r03: 9", "r04: 24", "r05: 13"]
row_y = hdr_y - ROW_GAP - ROW_H
for t in labels:
    box(SIDE_X, row_y, SIDE_W, ROW_H, t, face=SIDE, fs=9)
    row_y -= (ROW_H + ROW_GAP)

# total box (highlighted), with extra gap above
total_y = row_y - 0.15
box(SIDE_X, total_y, SIDE_W, ROW_H + 0.05, "Total GT: 62 trials",
    face=GT, fs=9.5)

# ----- title -----------------------------------------------------------------
ax.text(MAIN_CENTRE, 14.05,
        "Combined PRISMA-style flow across five systematic reviews",
        ha="center", va="center", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig("figure1_prisma.pdf", dpi=300, bbox_inches="tight")
plt.savefig("figure1_prisma.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Figure 1 saved.")
