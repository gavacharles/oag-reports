"""
Figure 3: GWR coefficient surfaces for land_and_right_of_way -- the one
outcome where GWR meaningfully beats the global model (AICc 82.8 vs
87.0, a difference >3). Local R^2 plus four local coefficient maps:
distance to Kampala, dependency ratio, and the two tenure dummies.
Districts where the local estimate is not significant (|t|<1.96) are
hatched, following the dataviz skill's texture-fill convention for the
accessibility/uncertainty channel.
"""
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

sys.path.insert(0, "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/07_visualization")
from viz_style import DIVERGING_BLUE_RED, INK_PRIMARY, INK_SECONDARY, SEQUENTIAL_BLUE, apply_style

apply_style()

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
gdf = gpd.read_file(f"{BASE}/08_gwr/gwr_local_coefficients_land.geojson")
OUT = f"{BASE}/08_gwr/figure3_gwr_land_coefficients.png"

diverging_cmap = LinearSegmentedColormap.from_list("div", DIVERGING_BLUE_RED)
sequential_cmap = LinearSegmentedColormap.from_list("seq", SEQUENTIAL_BLUE)

fig, axes = plt.subplots(1, 5, figsize=(24, 6))

# panel 1: local R^2 (sequential)
ax = axes[0]
gdf.plot(column="local_R2", ax=ax, cmap=sequential_cmap, edgecolor="white", linewidth=0.2, legend=True,
         legend_kwds={"shrink": 0.6, "label": "Local R²"})
ax.set_title("Local model fit (R²)", fontsize=11.5, color=INK_PRIMARY)
ax.axis("off")

VARS = [
    ("beta_distance_to_kampala_km", "sig_distance_to_kampala_km", "Distance to Kampala"),
    ("beta_dependency_ratio", "sig_dependency_ratio", "Dependency ratio"),
    ("beta_tenure_mailo", "sig_tenure_mailo", "Mailo tenure"),
    ("beta_tenure_freehold", "sig_tenure_freehold", "Freehold tenure"),
]

for ax, (beta_col, sig_col, label) in zip(axes[1:], VARS):
    vmax = gdf[beta_col].abs().quantile(0.95)  # clip extreme instability, note in caption
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    gdf.plot(column=beta_col, ax=ax, cmap=diverging_cmap, norm=norm, edgecolor="white", linewidth=0.2,
              legend=True, legend_kwds={"shrink": 0.6, "label": "Local β (std.)"})
    not_sig = gdf[~gdf[sig_col]]
    not_sig.plot(ax=ax, facecolor="none", edgecolor=INK_SECONDARY, hatch="//////", linewidth=0, alpha=0.35)
    n_sig = int(gdf[sig_col].sum())
    ax.set_title(f"{label}\n({n_sig}/135 districts sig., |t|>1.96)", fontsize=11.5, color=INK_PRIMARY)
    ax.axis("off")

fig.suptitle(
    "Geographically weighted regression: local coefficients for land/right-of-way dispute intensity\n"
    "(hatched = not statistically significant at that location; GWR AICc 82.8 vs. global OLS AICc 87.0)",
    fontsize=13, color=INK_PRIMARY, y=1.06,
)
fig.tight_layout()
fig.savefig(OUT, dpi=220, bbox_inches="tight")
print(f"saved {OUT}")
