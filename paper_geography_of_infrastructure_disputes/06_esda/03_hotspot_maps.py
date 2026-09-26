import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/06_esda"
gdf = gpd.read_file(f"{BASE}/district_driver_counts.geojson")
hotspots = pd.read_csv(f"{BASE}/getis_ord_hotspots.csv")

DRIVERS_TO_PLOT = ["land_and_right_of_way", "delayed_payments", "cost_overrun", "delay_time_overrun"]
LABELS = {
    "land_and_right_of_way": "Land / Right-of-Way",
    "delayed_payments": "Delayed Payments",
    "cost_overrun": "Cost Overrun",
    "delay_time_overrun": "Delay / Time Overrun",
}

fig, axes = plt.subplots(2, 2, figsize=(14, 14))
for ax, driver in zip(axes.flat, DRIVERS_TO_PLOT):
    sub = hotspots[hotspots["driver"] == driver].set_index("district")
    g = gdf.set_index("district").join(sub[["Gi_star_z", "hotspot_95", "hotspot_90"]])

    def classify(row):
        if row["hotspot_95"]:
            return "Hot spot (p<0.05)"
        if row["hotspot_90"]:
            return "Hot spot (p<0.10)"
        return "Not significant"

    g["cat"] = g.apply(classify, axis=1)
    colors = {"Hot spot (p<0.05)": "#d73027", "Hot spot (p<0.10)": "#fc8d59", "Not significant": "#f0f0f0"}
    g.plot(ax=ax, color=g["cat"].map(colors), edgecolor="white", linewidth=0.3)
    ax.set_title(f"{LABELS[driver]}\n(Getis-Ord Gi*, Queen contiguity, FDR-corrected)", fontsize=11)
    ax.axis("off")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors.values()]
    ax.legend(handles, colors.keys(), loc="lower left", fontsize=8, frameon=False)

fig.suptitle("District-level dispute-driver hot spots, 2017-2025 (project-level OAG audit findings)", fontsize=14)
fig.tight_layout()
fig.savefig(f"{BASE}/hotspot_maps.png", dpi=200, bbox_inches="tight")
print(f"saved {BASE}/hotspot_maps.png")
