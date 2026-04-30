"""Figure 3: per-field cross-domain accuracy heatmap (11 fields x 5 reviews).

Data source: reviews/PHASE2_FINAL_REPORT.md, Section 4.
"""
import matplotlib.pyplot as plt
import numpy as np

fields = [
    "first_author", "year", "intervention", "n_total",
    "primary_efficacy_outcome", "maintenance_weeks_ge_12", "phase",
    "n_active", "age_range_years", "n_placebo", "dose",
]
reviews = ["r01", "r02", "r03", "r04", "r05"]

# 4-model averages per field per review (% from Section 4)
data = np.array([
    [100.0, 100.0, 100.0, 100.0, 100.0],   # first_author (v2)
    [100.0, 100.0, 100.0,  95.3, 100.0],   # year
    [100.0, 100.0, 100.0, 100.0, 100.0],   # intervention
    [ 82.1, 100.0, 100.0,  91.9,  90.9],   # n_total
    [ 89.3,  96.4,  88.9,  73.2,  65.9],   # primary_efficacy_outcome
    [ 96.4,  78.6,  52.8,  88.4, 100.0],   # maintenance_weeks_ge_12
    [ 53.6,  60.7, 100.0,  66.1,  68.2],   # phase
    [ 82.1,  92.9,  69.4,  84.9,   0.0],   # n_active
    [ 64.3,  17.9,  58.3,  51.4,  61.4],   # age_range_years
    [ 78.6,  85.7,  38.9,  53.6,  31.8],   # n_placebo
    [ 85.7,  85.7,  38.9,  64.0,  15.9],   # dose
])

fig, ax = plt.subplots(figsize=(6.5, 6.0))
im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
ax.set_xticks(np.arange(len(reviews)))
ax.set_xticklabels(["r01\nEpil.", "r02\nCard.", "r03\nOnco.", "r04\nPsy.", "r05\nResp."], fontsize=9)
ax.set_yticks(np.arange(len(fields)))
ax.set_yticklabels(fields, fontsize=9)

for i in range(len(fields)):
    for j in range(len(reviews)):
        v = data[i, j]
        col = "black" if 25 <= v <= 75 else ("white" if v < 25 else "black")
        ax.text(j, i, f"{v:.0f}", ha="center", va="center", color=col, fontsize=8)

cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("4-model mean v2 accuracy (%)", fontsize=9)
ax.set_title("Per-field cross-domain extraction accuracy\n(11 schema fields $\\times$ 5 reviews)", fontsize=10)

plt.tight_layout()
plt.savefig("figure3_field_heatmap.pdf", bbox_inches="tight")
plt.savefig("figure3_field_heatmap.png", bbox_inches="tight", dpi=200)
print("Figure 3 saved.")
