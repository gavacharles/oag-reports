"""
Explanatory spatial regression, per the outline's Methods section 4:
OLS baseline -> spatial diagnostics (Moran's I on residuals, Lagrange
Multiplier tests) -> spatial lag and spatial error models -> compare.
Then a Random Forest + SHAP robustness check on the same variables
(handles non-linearity/interactions that a linear spatial model can't,
and doesn't assume the same functional form).

DV: log1p(n_projects) -- overall dispute-driver intensity per district.
Also run for the two strongest ESDA categories (land_and_right_of_way,
delay_time_overrun) as secondary DVs.

This is a 135-observation cross-sectional model on a genuinely small,
zero-inflated count outcome -- results should be read as exploratory/
descriptive of association, not causal, and are reported with that
framing throughout.
"""
import warnings

import geopandas as gpd
import libpysal
import numpy as np
import pandas as pd
from spreg import OLS, ML_Error, ML_Lag
from esda.moran import Moran

warnings.filterwarnings("ignore")

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
DATA = f"{BASE}/06_esda/district_regression_dataset.csv"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT_DIR = f"{BASE}/06_esda"

df = pd.read_csv(DATA)
gdf = gpd.read_file(DISTRICTS)[["adm2_name", "geometry"]].rename(columns={"adm2_name": "district"})
df = gdf.merge(df, on="district", how="inner")
assert len(df) == 135

w = libpysal.weights.Queen.from_dataframe(df, use_index=False)
w.transform = "r"

IV_COLS = [
    "distance_to_kampala_km", "elevation_m", "mean_annual_rainfall_mm",
    "log_population", "dependency_ratio", "rural_pop_perc", "rural_access_index_pct",
]
df["tenure_mailo"] = (df["land_tenure_proxy"] == "mailo").astype(int)
df["tenure_freehold"] = (df["land_tenure_proxy"] == "freehold").astype(int)
IV_COLS_FULL = IV_COLS + ["tenure_mailo", "tenure_freehold"]

X = df[IV_COLS_FULL].values
# standardize IVs for interpretable, comparable coefficients
X_std = (X - X.mean(axis=0)) / X.std(axis=0)

DVS = {
    "n_projects": "log1p_n_projects",
    "land_and_right_of_way": "log1p_land",
    "delay_time_overrun": "log1p_delay",
}

all_summaries = []
for raw_dv, dv_name in DVS.items():
    y = np.log1p(df[raw_dv].values).reshape(-1, 1)
    print(f"\n{'='*70}\nDV = {dv_name} (log1p of {raw_dv})\n{'='*70}")

    ols = OLS(y, X_std, w=w, spat_diag=True, moran=True, name_y=dv_name, name_x=IV_COLS_FULL)
    print(ols.summary)

    resid_moran = Moran(ols.u.flatten(), w, permutations=999)
    print(f"\nMoran's I on OLS residuals: I={resid_moran.I:.4f}, p_sim={resid_moran.p_sim:.4f}")

    lm_lag_p = ols.lm_lag[1] if hasattr(ols, "lm_lag") else None
    lm_err_p = ols.lm_error[1] if hasattr(ols, "lm_error") else None
    print(f"LM-lag p={lm_lag_p}, LM-error p={lm_err_p}")

    # fit both spatial models regardless, report both, let LM tests guide which is preferred
    lag_model = ML_Lag(y, X_std, w=w, name_y=dv_name, name_x=IV_COLS_FULL)
    err_model = ML_Error(y, X_std, w=w, name_y=dv_name, name_x=IV_COLS_FULL)

    print("\n--- Spatial Lag (ML) ---")
    print(lag_model.summary)
    print("\n--- Spatial Error (ML) ---")
    print(err_model.summary)

    for model_name, m in [("OLS", ols), ("Spatial_Lag", lag_model), ("Spatial_Error", err_model)]:
        coefs = m.betas.flatten()
        names = ["CONSTANT"] + IV_COLS_FULL + (["W_lag_y"] if model_name == "Spatial_Lag" else []) + (["lambda"] if model_name == "Spatial_Error" else [])
        se = np.sqrt(np.diag(m.vm)) if hasattr(m, "vm") and m.vm is not None else [None] * len(coefs)
        for nm, c, s in zip(names, coefs, se):
            all_summaries.append({
                "dv": dv_name, "model": model_name, "variable": nm,
                "coef": round(float(c), 4), "se": round(float(s), 4) if s is not None else None,
                "pseudo_r2": round(float(getattr(m, "pr2", np.nan)), 4) if hasattr(m, "pr2") else None,
            })

    all_summaries.append({"dv": dv_name, "model": "OLS", "variable": "MORAN_I_RESIDUALS",
                           "coef": round(resid_moran.I, 4), "se": round(resid_moran.p_sim, 4), "pseudo_r2": None})
    all_summaries.append({"dv": dv_name, "model": "OLS", "variable": "LM_LAG_P", "coef": lm_lag_p, "se": None, "pseudo_r2": None})
    all_summaries.append({"dv": dv_name, "model": "OLS", "variable": "LM_ERROR_P", "coef": lm_err_p, "se": None, "pseudo_r2": None})

res_df = pd.DataFrame(all_summaries)
res_df.to_csv(f"{OUT_DIR}/spatial_regression_results.csv", index=False)
print(f"\n\nSaved -> {OUT_DIR}/spatial_regression_results.csv")

df.drop(columns="geometry").to_csv(f"{OUT_DIR}/district_regression_dataset_final.csv", index=False)
