"""
Figure 2: District-level Getis-Ord Gi* hot/cold spot maps, all 8 driver
categories, using the validated diverging blue<->red palette (red=hot,
blue=cold, neutral gray=not significant) instead of the ad-hoc red/orange
scheme in the first-pass version.
"""
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/07_visualization")
from viz_style import DRIVER_LABELS, INK_PRIMARY, INK_SECONDARY, apply_style

apply_style()

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
gdf = gpd.read_file(f"{BASE}/06_esda/district_driver_counts.geojson")
hotspots = pd.read_csv(f"{BASE}/06_esda/getis_ord_hotspots.csv")
OUT = f"{BASE}/07_visualization/figure2_hotspot_maps_all8.png"

DRIVERS = [
    "land_and_right_of_way", "delay_time_overrun", "procurement_irregularities",
    "delayed_payments", "contract_management", "cost_overrun",
    "governance_and_controls", "claims_and_disputes",
]

# diverging classes, red=hot / blue=cold / gray=n.s.
CLASS_COLORS = {
    "Hot (p<0.05)": "#c62a29",
    "Hot (p<0.10)": "#eb6f66",
    "Not significant": "#f0efec",
    "Cold (p<0.10)": "#b7d3f6",
    "Cold (p<0.05)": "#1c5cab",
}


def classify(row):
    if row["hotspot_95"]:
        return "Hot (p<0.05)"
    if row["hotspot_90"]:
        return "Hot (p<0.10)"
    if row["coldspot_95"]:
        return "Cold (p<0.05)"
    return "Not significant"


fig, axes = plt.subplots(2, 4, figsize=(20, 11))
for ax, driver in zip(axes.flat, DRIVERS):
    sub = hotspots[hotspots["driver"] == driver].set_index("district")
    g = gdf.set_index("district").join(sub[["Gi_star_z", "hotspot_95", "hotspot_90", "coldspot_95"]])
    g["cat"] = g.apply(classify, axis=1)
    g.plot(ax=ax, color=g["cat"].map(CLASS_COLORS), edgecolor="white", linewidth=0.25)
    n_hot = int(g["hotspot_95"].sum())
    ax.set_title(f"{DRIVER_LABELS[driver]}\n({n_hot} district{'s' if n_hot != 1 else ''} sig. hot, p<0.05)",
                 fontsize=10.5, color=INK_PRIMARY)
    ax.axis("off")

handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in CLASS_COLORS.values()]
fig.legend(handles, CLASS_COLORS.keys(), loc="lower center", ncol=5, fontsize=9.5, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("District-level dispute-driver hot spots, 2017-2025 (Getis-Ord Gi*, Queen contiguity, FDR-corrected)",
             fontsize=14, color=INK_PRIMARY, y=1.01)
fig.tight_layout()
fig.savefig(OUT, dpi=220, bbox_inches="tight")
print(f"saved {OUT}")
