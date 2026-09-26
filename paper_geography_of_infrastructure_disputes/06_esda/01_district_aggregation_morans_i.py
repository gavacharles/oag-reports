"""
District-level aggregation of dispute-driver project counts, and global
Moran's I per driver category, using Queen contiguity weights over the
135 OCHA COD-AB district polygons.

Honest caveat up front: only 261/283 geocoded projects have a usable
district assignment, spread across 90 distinct districts out of 135
nationally -- so roughly a third of districts have zero observed
projects. This is expected given OAG audit coverage is not a census (not
every project is audited every year), but it does mean Moran's I here is
likely to have limited power; that is reported honestly below rather
than only running the test on categories where it happens to come out
significant.
"""
import geopandas as gpd
import libpysal
import numpy as np
import pandas as pd
from esda.moran import Moran

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
PROJECTS = f"{BASE}/05_covariates/project_level_with_covariates.csv"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT_DIR = f"{BASE}/06_esda"

DRIVERS = [
    "delay_time_overrun", "cost_overrun", "claims_and_disputes",
    "land_and_right_of_way", "contract_management", "delayed_payments",
    "governance_and_controls", "procurement_irregularities",
]

districts = gpd.read_file(DISTRICTS)[["adm2_name", "adm2_pcode", "geometry"]].rename(
    columns={"adm2_name": "district"}
)

df = pd.read_csv(PROJECTS)
df = df[df["district_final"].notna()].copy()
df["drivers_mentioned"] = df["drivers_mentioned"].fillna("")

# one row per (project, driver) for counting
rows = []
for _, r in df.iterrows():
    dist = r["district_final"]
    if ";" in str(dist):  # cross-boundary project (Ssezibwa swamp crossing) -- count in both
        dist_list = [d.strip() for d in dist.split(";")]
    else:
        dist_list = [dist]
    drivers_here = [d for d in DRIVERS if d in r["drivers_mentioned"]]
    for d_name in dist_list:
        rows.append({"district": d_name, "n_projects": 1, **{d: (dr in drivers_here) for d, dr in zip(DRIVERS, DRIVERS)}})

agg_input = pd.DataFrame(rows)
district_counts = agg_input.groupby("district").agg({**{"n_projects": "sum"}, **{d: "sum" for d in DRIVERS}}).reset_index()

merged = districts.merge(district_counts, on="district", how="left")
for c in ["n_projects"] + DRIVERS:
    merged[c] = merged[c].fillna(0)

print(f"{len(merged)} districts total, {(merged['n_projects']>0).sum()} with >=1 project, "
      f"{(merged['n_projects']==0).sum()} with zero")

merged.to_file(f"{OUT_DIR}/district_driver_counts.geojson", driver="GeoJSON")
merged.drop(columns="geometry").to_csv(f"{OUT_DIR}/district_driver_counts.csv", index=False)

# Queen contiguity spatial weights
w = libpysal.weights.Queen.from_dataframe(merged, use_index=False)
w.transform = "r"
n_islands = len(w.islands)
print(f"Queen contiguity weights: {w.n} units, {n_islands} islands (no neighbours)")

results = []
for var in ["n_projects"] + DRIVERS:
    y = merged[var].values.astype(float)
    if y.std() == 0:
        print(f"{var}: constant (all zero or all same) -- Moran's I undefined, skipping")
        continue
    mi = Moran(y, w, permutations=999)
    results.append({
        "variable": var, "morans_I": round(mi.I, 4), "expected_I": round(mi.EI, 4),
        "p_value_sim": round(mi.p_sim, 4), "z_sim": round(mi.z_sim, 3),
        "n_nonzero_districts": int((y > 0).sum()),
    })
    print(f"{var:30s} I={mi.I:.4f}  E[I]={mi.EI:.4f}  p_sim={mi.p_sim:.4f}  "
          f"z={mi.z_sim:.3f}  (n_nonzero={int((y>0).sum())})")

res_df = pd.DataFrame(results)
res_df.to_csv(f"{OUT_DIR}/global_morans_i_results.csv", index=False)
print(f"\nSaved -> {OUT_DIR}/global_morans_i_results.csv")
print(f"Saved -> {OUT_DIR}/district_driver_counts.csv / .geojson")
