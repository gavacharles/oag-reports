"""
Geographically Weighted Regression (GWR), the alternative to spatial
lag/error models named in the outline's Methods 4. Where the global
spatial-lag/error models (06_esda) ask "is there one relationship that
holds everywhere," GWR asks "does the relationship itself vary across
the country" -- fitting a local regression at every district centroid,
weighted by distance (adaptive bisquare kernel, bandwidth chosen by
golden-section AICc minimisation, standard mgwr practice).

Same DV/IV set as the global models, for direct comparability:
DV = log1p(n_projects); IVs = distance to Kampala, elevation, rainfall,
log population, dependency ratio, rural population %, Rural Access
Index, and the land-tenure proxy (mailo/freehold dummies).
"""
import geopandas as gpd
import numpy as np
import pandas as pd
from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
DATA = f"{BASE}/06_esda/district_regression_dataset_final.csv"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT_DIR = f"{BASE}/08_gwr"

df = pd.read_csv(DATA)
gdf = gpd.read_file(DISTRICTS)[["adm2_name", "geometry"]].rename(columns={"adm2_name": "district"})
df = gdf.merge(df, on="district", how="inner")
df["cen"] = df.geometry.centroid
coords = list(zip(df["cen"].x, df["cen"].y))

IV_COLS = [
    "distance_to_kampala_km", "elevation_m", "mean_annual_rainfall_mm",
    "log_population", "dependency_ratio", "rural_pop_perc", "rural_access_index_pct",
    "tenure_mailo", "tenure_freehold",
]
X = df[IV_COLS].values
X_std = (X - X.mean(axis=0)) / X.std(axis=0)
y = np.log1p(df["n_projects"].values).reshape(-1, 1)

print("Selecting bandwidth (golden-section AICc search, adaptive bisquare)...")
sel = Sel_BW(coords, y, X_std)
bw = sel.search()
print(f"Selected bandwidth: {bw:.1f} nearest neighbours (of {len(df)} districts)")

gwr = GWR(coords, y, X_std, bw)
results = gwr.fit()

print(results.summary())

# local R^2 and local coefficients per district
local_r2 = results.localR2.flatten()
params = results.params  # (n, n_vars+1) incl. intercept
tvals = results.tvalues

out = df[["district"]].copy()
out["local_R2"] = local_r2
out["intercept"] = params[:, 0]
for i, col in enumerate(IV_COLS):
    out[f"beta_{col}"] = params[:, i + 1]
    out[f"t_{col}"] = tvals[:, i + 1]
    out[f"sig_{col}"] = np.abs(tvals[:, i + 1]) > 1.96

out.to_csv(f"{OUT_DIR}/gwr_local_coefficients.csv", index=False)

# save with geometry for mapping
gdf_out = df[["district", "geometry"]].merge(out, on="district")
gdf_out.to_file(f"{OUT_DIR}/gwr_local_coefficients.geojson", driver="GeoJSON")

print(f"\nSaved -> {OUT_DIR}/gwr_local_coefficients.csv / .geojson")
print(f"\nGWR AICc: {results.aicc:.2f}  |  Global OLS AICc for comparison: see 06_esda spatial_regression_results.csv")
print(f"local R^2 range: {local_r2.min():.3f} to {local_r2.max():.3f} (mean {local_r2.mean():.3f})")

# global vs GWR model comparison via AICc (lower is better)
from spreg import OLS
ols = OLS(y, X_std)
print(f"\nGlobal OLS AICc: {ols.aic:.2f}")
print(f"GWR AICc:        {results.aicc:.2f}")
print("(GWR is preferred over global OLS if its AICc is meaningfully lower -- "
      "conventionally a difference of >3 is considered meaningful)")

with open(f"{OUT_DIR}/gwr_summary.txt", "w") as f:
    f.write(f"Selected bandwidth: {bw:.1f} nearest neighbours of {len(df)} districts\n")
    f.write(f"Global OLS AICc: {ols.aic:.2f}\n")
    f.write(f"GWR AICc: {results.aicc:.2f}\n")
    f.write(f"Local R2 range: {local_r2.min():.3f} to {local_r2.max():.3f} (mean {local_r2.mean():.3f})\n\n")
    f.write(str(results.summary()))
print(f"Saved -> {OUT_DIR}/gwr_summary.txt")
