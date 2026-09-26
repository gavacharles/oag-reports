"""
Two robustness checks a Q1 reviewer will expect and the original pipeline
didn't run:

1. Alternative spatial weights: does Moran's I / the spatial-lag result
   for the three modelled outcomes hold under k-nearest-neighbour (k=5,
   k=8) weights, not just Queen contiguity? Contiguity weights can behave
   oddly for irregularly-sized districts; KNN is the standard alternative
   check.

2. Negative Binomial regression: the main models use log1p(count) + OLS
   for comparability with the spatial-econometrics toolkit (spreg/mgwr
   don't natively support count-GLM spatial models), but the true DV is
   a sparse, zero-inflated count. A standard (non-spatial) Negative
   Binomial GLM on the raw counts is run here as a distributional
   robustness check: do the same variables come out significant with
   the same sign under a model built for count data specifically?
"""
import warnings

import geopandas as gpd
import libpysal
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from esda.moran import Moran

warnings.filterwarnings("ignore")

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
DATA = f"{BASE}/06_esda/district_regression_dataset_final.csv"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT_DIR = f"{BASE}/06_esda"

df = pd.read_csv(DATA)
gdf = gpd.read_file(DISTRICTS)[["adm2_name", "geometry"]].rename(columns={"adm2_name": "district"})
df = gdf.merge(df, on="district", how="inner")
assert len(df) == 135

IV_COLS = [
    "distance_to_kampala_km", "elevation_m", "mean_annual_rainfall_mm",
    "log_population", "dependency_ratio", "rural_pop_perc", "rural_access_index_pct",
    "tenure_mailo", "tenure_freehold",
]
DVS = {"n_projects": "n_projects", "land_and_right_of_way": "land_and_right_of_way", "delay_time_overrun": "delay_time_overrun"}

# ---------------- 1. alternative spatial weights ----------------
w_queen = libpysal.weights.Queen.from_dataframe(df, use_index=False)
w_queen.transform = "r"
w_knn5 = libpysal.weights.KNN.from_dataframe(df, k=5)
w_knn5.transform = "r"
w_knn8 = libpysal.weights.KNN.from_dataframe(df, k=8)
w_knn8.transform = "r"

weights_results = []
for raw_dv in DVS:
    y = np.log1p(df[raw_dv].values)
    for wname, w in [("Queen", w_queen), ("KNN-5", w_knn5), ("KNN-8", w_knn8)]:
        mi = Moran(y, w, permutations=999)
        weights_results.append({
            "dv": raw_dv, "weights": wname, "morans_I": round(mi.I, 4),
            "p_sim": round(mi.p_sim, 4), "z_sim": round(mi.z_sim, 3),
        })
        print(f"{raw_dv:28s} {wname:8s} I={mi.I:.4f} p={mi.p_sim:.4f}")

pd.DataFrame(weights_results).to_csv(f"{OUT_DIR}/robustness_alt_weights.csv", index=False)
print(f"\nSaved -> {OUT_DIR}/robustness_alt_weights.csv")

# ---------------- 2. Negative Binomial GLM ----------------
nb_results = []
for raw_dv in DVS:
    d = df.copy()
    for c in IV_COLS:
        d[c] = (d[c] - d[c].mean()) / d[c].std()
    formula = f"{raw_dv} ~ " + " + ".join(IV_COLS)
    try:
        model = smf.glm(formula=formula, data=d, family=sm.families.NegativeBinomial()).fit()
    except Exception as e:
        print(f"NB failed for {raw_dv}: {e}")
        continue
    print(f"\n=== Negative Binomial: {raw_dv} ===")
    print(model.summary())
    for var in ["Intercept"] + IV_COLS:
        nb_results.append({
            "dv": raw_dv, "variable": var,
            "coef": round(model.params.get(var, np.nan), 4),
            "se": round(model.bse.get(var, np.nan), 4),
            "p_value": round(model.pvalues.get(var, np.nan), 4),
        })
    nb_results.append({"dv": raw_dv, "variable": "pseudo_R2_deviance",
                        "coef": round(1 - model.deviance / model.null_deviance, 4), "se": None, "p_value": None})

pd.DataFrame(nb_results).to_csv(f"{OUT_DIR}/robustness_negative_binomial.csv", index=False)
print(f"\nSaved -> {OUT_DIR}/robustness_negative_binomial.csv")
