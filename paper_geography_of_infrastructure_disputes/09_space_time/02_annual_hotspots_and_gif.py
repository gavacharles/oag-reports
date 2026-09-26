"""
Per-year Getis-Ord Gi* (total project count, all drivers pooled -- the
only variable with enough non-zero cells per year to be worth mapping at
all) plus a simplified emerging hot-spot classification per district
(Mann-Kendall trend on each district's yearly Gi* z-score series,
ESRI's standard approach), rendered as a 9-frame annual GIF.

Years 2017 and 2020 have zero non-zero district-year cells in this
corpus (2020's OAG "report" is actually an internal strategic-planning
document, not an audit report -- flagged during project extraction) and
are skipped in the per-year Gi* computation but shown in the animation
as explicitly blank/no-data frames rather than silently omitted.
"""
import sys

import geopandas as gpd
import imageio.v2 as imageio
import libpysal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymannkendall as mk
from esda.getisord import G_Local
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/07_visualization")
from viz_style import DIVERGING_BLUE_RED, INK_MUTED, INK_PRIMARY, INK_SECONDARY, apply_style

apply_style()

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
PANEL = f"{BASE}/09_space_time/annual_district_counts.csv"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT_DIR = f"{BASE}/09_space_time"
FRAMES_DIR = f"{OUT_DIR}/frames"
import os
os.makedirs(FRAMES_DIR, exist_ok=True)

YEARS = list(range(2017, 2026))
NO_DATA_YEARS = {2017, 2020}

panel = pd.read_csv(PANEL)
districts = gpd.read_file(DISTRICTS)[["adm2_name", "geometry"]].rename(columns={"adm2_name": "district"})
w = libpysal.weights.Queen.from_dataframe(districts, use_index=False)
w.transform = "r"

diverging_cmap = LinearSegmentedColormap.from_list("div", DIVERGING_BLUE_RED)

z_by_year = {}
for yr in YEARS:
    if yr in NO_DATA_YEARS:
        continue
    yr_data = panel[panel["year"] == yr].set_index("district").reindex(districts["district"]).fillna(0)
    y = yr_data["n_projects"].values.astype(float)
    if y.std() == 0:
        continue
    g = G_Local(y, w, transform="R", permutations=999, star=True)
    z_by_year[yr] = g.Zs

# Mann-Kendall trend per district on its available yearly z-score series
z_matrix = pd.DataFrame(z_by_year, index=districts["district"])
trend_results = []
for dist in z_matrix.index:
    series = z_matrix.loc[dist].dropna().values
    if len(series) < 4:
        trend_results.append({"district": dist, "trend": "insufficient data", "mk_p": None})
        continue
    try:
        result = mk.original_test(series)
        trend_results.append({"district": dist, "trend": result.trend, "mk_p": round(result.p, 4)})
    except Exception:
        trend_results.append({"district": dist, "trend": "error", "mk_p": None})

trend_df = pd.DataFrame(trend_results)
trend_df.to_csv(f"{OUT_DIR}/emerging_hotspot_trends.csv", index=False)
print("Mann-Kendall trend classification (per-district Gi* z-score series, 2017-2025):")
print(trend_df["trend"].value_counts())

vmax = np.nanmax(np.abs(z_matrix.values)) if z_matrix.size else 3.0

# ---------------- render annual frames ----------------
frame_paths = []
for yr in YEARS:
    fig, ax = plt.subplots(figsize=(8, 9))
    if yr in NO_DATA_YEARS:
        districts.plot(ax=ax, color="#ececec", edgecolor="white", linewidth=0.2)
        ax.text(0.5, 0.5, "No audit-year\nreferences in corpus", transform=ax.transAxes,
                ha="center", va="center", fontsize=13, color=INK_SECONDARY)
    else:
        g = districts.copy()
        g["z"] = z_by_year[yr]
        g.plot(column="z", ax=ax, cmap=diverging_cmap, vmin=-vmax, vmax=vmax, edgecolor="white", linewidth=0.2)
    ax.set_title(f"Dispute-driver project intensity, {yr}\n(Getis-Ord Gi*, all drivers pooled)",
                 fontsize=13.5, color=INK_PRIMARY)
    ax.axis("off")
    fig.tight_layout()
    fp = f"{FRAMES_DIR}/frame_{yr}.png"
    fig.savefig(fp, dpi=150, bbox_inches="tight")
    plt.close(fig)
    frame_paths.append(fp)
    print(f"rendered {yr}")

images = [imageio.imread(fp) for fp in frame_paths]
gif_path = f"{OUT_DIR}/emerging_hotspots_2017_2025.gif"
imageio.mimsave(gif_path, images, duration=1200, loop=0)
print(f"\nSaved animated GIF -> {gif_path}")
