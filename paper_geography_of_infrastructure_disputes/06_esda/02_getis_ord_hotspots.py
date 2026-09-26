"""
Local Getis-Ord Gi* hot-spot analysis per driver category, at the
district level (Queen contiguity weights, same as the global Moran's I
step) -- identifies WHICH districts are statistically significant
hot spots (high values surrounded by high values) vs cold spots, at the
90% / 95% / 99% confidence levels, FDR-corrected across the simultaneous
per-district tests within each category.
"""
import geopandas as gpd
import libpysal
import pandas as pd
from esda.getisord import G_Local
from statsmodels.stats.multitest import multipletests

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
OUT_DIR = f"{BASE}/06_esda"

DRIVERS = [
    "n_projects", "delay_time_overrun", "cost_overrun", "claims_and_disputes",
    "land_and_right_of_way", "contract_management", "delayed_payments",
    "governance_and_controls", "procurement_irregularities",
]

gdf = gpd.read_file(f"{OUT_DIR}/district_driver_counts.geojson")
w = libpysal.weights.Queen.from_dataframe(gdf, use_index=False)
w.transform = "r"

all_results = []
for var in DRIVERS:
    y = gdf[var].values.astype(float)
    if y.std() == 0:
        continue
    g = G_Local(y, w, transform="R", permutations=999, star=True)
    p_fdr = multipletests(g.p_sim, method="fdr_bh")[1]
    for i, district in enumerate(gdf["district"]):
        all_results.append({
            "driver": var, "district": district, "value": y[i],
            "Gi_star_z": round(g.Zs[i], 3), "p_sim": round(g.p_sim[i], 4),
            "p_fdr": round(p_fdr[i], 4),
            "hotspot_95": bool((g.Zs[i] > 0) and (p_fdr[i] < 0.05)),
            "hotspot_90": bool((g.Zs[i] > 0) and (p_fdr[i] < 0.10)),
            "coldspot_95": bool((g.Zs[i] < 0) and (p_fdr[i] < 0.05)),
        })
    n_hot95 = sum(1 for r in all_results if r["driver"] == var and r["hotspot_95"])
    print(f"{var:30s} {n_hot95} district(s) significant hot spot at FDR<0.05")

res = pd.DataFrame(all_results)
res.to_csv(f"{OUT_DIR}/getis_ord_hotspots.csv", index=False)
print(f"\nSaved -> {OUT_DIR}/getis_ord_hotspots.csv")

print("\n=== significant hot spots (FDR<0.05), by driver ===")
sig = res[res["hotspot_95"]].sort_values(["driver", "Gi_star_z"], ascending=[True, False])
print(sig[["driver", "district", "value", "Gi_star_z", "p_fdr"]].to_string(index=False))
