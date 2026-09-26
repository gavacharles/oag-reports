"""
Figure 1: National distribution of geocoded infrastructure-dispute
projects, 2017-2025. Points sized by mention count, coloured by primary
driver family (fixed categorical order, CVD-validated). Road/transmission
-line projects drawn as straight-line proxies between named endpoints,
clearly distinguished from point facilities.
"""
import ast
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import LineString, Point

sys.path.insert(0, "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/07_visualization")
from viz_style import DRIVER_COLORS, DRIVER_LABELS, INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE, apply_style

apply_style()

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
PROJECTS = f"{BASE}/05_covariates/project_level_with_covariates.csv"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT = f"{BASE}/07_visualization/figure1_national_distribution.png"

DRIVER_ORDER = [
    "land_and_right_of_way", "delay_time_overrun", "procurement_irregularities",
    "delayed_payments", "contract_management", "cost_overrun",
    "governance_and_controls", "claims_and_disputes",
]

districts = gpd.read_file(DISTRICTS)
df = pd.read_csv(PROJECTS)


def primary_driver(s):
    if pd.isna(s):
        return None
    drivers_here = str(s).split(";")
    for d in DRIVER_ORDER:
        if d in drivers_here:
            return d
    return None


df["primary"] = df["drivers_mentioned"].apply(primary_driver)

fig, ax = plt.subplots(figsize=(11, 12))
districts.plot(ax=ax, color=SURFACE, edgecolor="#d8d6cd", linewidth=0.4)
districts.dissolve().boundary.plot(ax=ax, color=INK_MUTED, linewidth=0.8)

# lines first (underneath points)
n_lines = 0
for _, r in df.iterrows():
    if pd.notna(r.get("lat1")) and pd.notna(r.get("lon1")) and pd.notna(r.get("lat2")) and pd.notna(r.get("lon2")):
        color = DRIVER_COLORS.get(r["primary"], INK_MUTED)
        ax.plot([r["lon1"], r["lon2"]], [r["lat1"], r["lat2"]], color=color, linewidth=1.6, alpha=0.75, solid_capstyle="round", zorder=3)
        n_lines += 1

# points
plotted_by_driver = {d: 0 for d in DRIVER_ORDER}
for _, r in df.iterrows():
    if pd.notna(r.get("lat")) and pd.notna(r.get("lon")):
        color = DRIVER_COLORS.get(r["primary"], INK_MUTED)
        size = 18 + 10 * min(r.get("n_mentions", 1), 6)
        ax.scatter(r["lon"], r["lat"], s=size, color=color, edgecolor="white", linewidth=0.5, alpha=0.88, zorder=4)
        if r["primary"] in plotted_by_driver:
            plotted_by_driver[r["primary"]] += 1

ax.set_xlim(29.3, 35.2)
ax.set_ylim(-1.6, 4.4)
ax.axis("off")
ax.set_title(
    "Geocoded infrastructure-dispute projects, Uganda 2017-2025\n"
    f"(n=238 geocoded of 283 canonical projects; points = facilities, lines = road/transmission corridors)",
    fontsize=13, color=INK_PRIMARY, loc="left", pad=14,
)

handles = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=DRIVER_COLORS[d], markersize=9, label=DRIVER_LABELS[d])
    for d in DRIVER_ORDER
]
ax.legend(handles=handles, loc="lower left", fontsize=9, title="Primary dispute driver", title_fontsize=9,
          bbox_to_anchor=(0.0, 0.0), frameon=False)

ax.annotate("Kampala", xy=(32.5811, 0.3136), fontsize=8.5, color=INK_SECONDARY, xytext=(3, 3), textcoords="offset points")
ax.scatter([32.5811], [0.3136], marker="*", s=90, color=INK_PRIMARY, zorder=5)

fig.tight_layout()
fig.savefig(OUT, dpi=250, bbox_inches="tight")
print(f"saved {OUT}")
print(f"plotted {n_lines} line-geometry projects and {sum(plotted_by_driver.values())} point projects with a driver")
print(plotted_by_driver)
