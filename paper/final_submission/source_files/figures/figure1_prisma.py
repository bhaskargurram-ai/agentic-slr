"""Figure 1: PRISMA-style flow aggregated across 5 reviews.

Compact 3-column layout — every column adjacent to the next so no box
floats in empty space:

    [exclusions]  ->  [main flow]   [GT sidebar]
       2.5 wide        5.5 wide        2.6 wide

Boxes are bigger than their text so labels never touch borders.
Sidebar rows have explicit gaps between them.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# canvas
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 12)
ax.set_ylim(0, 13.6)
ax.axis("off")

MAIN = "#E8EEF6"
GT   = "#FAF1D9"
LOSS = "#FBE9E7"
SIDE = "#F0F0F0"

BOX_KW = dict(boxstyle="round,pad=0.22", linewidth=1.0, edgecolor="black")


def box(x, y, w, h, text, face=MAIN, fs=10):
    p = FancyBboxPatch((x, y), w, h, facecolor=face, **BOX_KW)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, linespacing=1.25)


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


# === geometry ================================================================
LOSS_X, LOSS_W   = 0.20, 2.50
MAIN_X, MAIN_W   = 3.05, 5.55
SIDE_X, SIDE_W   = 9.00, 2.85
MAIN_CENTRE = MAIN_X + MAIN_W / 2

H = 1.10
GAP = 0.65

# === main flow ===============================================================
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

y_top = 12.10
ys = []
for i, (txt, face) in enumerate(stages):
    y = y_top - i * (H + GAP)
    ys.append(y)
    box(MAIN_X, y, MAIN_W, H, txt, face=face)

for i in range(len(stages) - 1):
    varrow(MAIN_CENTRE, ys[i], ys[i + 1] + H)

# === exclusions (left) =======================================================
LOSS_H = 0.95
loss_items = [
    (1, "Excluded by abstract screener:\n2,531 records"),
    (3, "Excluded at full-text stage:\n1,554 records"),
    (5, "Removed at dedup\n(secondary publications):\n103 records"),
]
for stage_idx, txt in loss_items:
    target_y_centre = (ys[stage_idx - 1] + ys[stage_idx] + H) / 2
    by = target_y_centre - LOSS_H / 2
    box(LOSS_X, by, LOSS_W, LOSS_H, txt, face=LOSS, fs=8.5)
    harrow(LOSS_X + LOSS_W, target_y_centre, MAIN_X)

# === GT sidebar (right) ======================================================
HDR_H = 0.65
ROW_H = 0.55
ROW_GAP = 0.12

# anchor sidebar header level with TOP of first main-flow box
sb_top = ys[0] + H
hdr_y = sb_top - HDR_H
box(SIDE_X, hdr_y, SIDE_W, HDR_H, "GT trials per review",
    face=SIDE, fs=10.5)

labels = ["r01:  7", "r02:  9", "r03:  9", "r04: 24", "r05: 13"]
row_y = hdr_y - ROW_GAP - ROW_H
for t in labels:
    box(SIDE_X, row_y, SIDE_W, ROW_H, t, face=SIDE, fs=10)
    row_y -= (ROW_H + ROW_GAP)

total_y = row_y - 0.20
box(SIDE_X, total_y, SIDE_W, ROW_H + 0.10,
    "Total GT: 62 trials", face=GT, fs=10.5)

# === title ===================================================================
ax.text(MAIN_CENTRE, 13.20,
        "Combined PRISMA-style flow across five systematic reviews",
        ha="center", va="center", fontsize=12.5, fontweight="bold")

plt.tight_layout()
plt.savefig("figure1_prisma.pdf", dpi=300, bbox_inches="tight")
plt.savefig("figure1_prisma.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Figure 1 saved.")
