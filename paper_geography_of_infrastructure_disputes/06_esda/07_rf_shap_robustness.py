"""
Random Forest + SHAP robustness check on the same district-level
variables as the spatial regression, per the outline's Methods section 4.
Purpose: check whether the linear spatial models' findings hold up under
a non-parametric method that doesn't assume linearity/additivity -- and
flag any important non-linear relationships or interactions the linear
models would miss. Given only 135 observations, this is a modest,
descriptive check (leave-one-out CV for honesty about small-n limits),
not a claim of strong predictive power.
"""
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import r2_score

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/06_esda"
DATA = f"{BASE}/district_regression_dataset_final.csv"
OUT_DIR = BASE

df = pd.read_csv(DATA)

IV_COLS = [
    "distance_to_kampala_km", "elevation_m", "mean_annual_rainfall_mm",
    "log_population", "dependency_ratio", "rural_pop_perc", "rural_access_index_pct",
    "tenure_mailo", "tenure_freehold",
]
DVS = {"n_projects": "log1p_n_projects", "land_and_right_of_way": "log1p_land", "delay_time_overrun": "log1p_delay"}

X = df[IV_COLS].values
importance_rows = []
shap_rows = []

for raw_dv, dv_name in DVS.items():
    y = np.log1p(df[raw_dv].values)
    rf = RandomForestRegressor(n_estimators=500, max_depth=4, min_samples_leaf=5, random_state=42)

    loo_pred = cross_val_predict(rf, X, y, cv=LeaveOneOut())
    r2_loo = r2_score(y, loo_pred)
    print(f"{dv_name}: leave-one-out R^2 = {r2_loo:.3f}")

    rf.fit(X, y)
    importances = dict(zip(IV_COLS, rf.feature_importances_))
    for var, imp in sorted(importances.items(), key=lambda kv: -kv[1]):
        importance_rows.append({"dv": dv_name, "variable": var, "gini_importance": round(float(imp), 4), "loo_r2": round(r2_loo, 4)})

    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X)
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    for var, sv in sorted(zip(IV_COLS, mean_abs_shap), key=lambda kv: -kv[1]):
        # sign of association: correlation between the variable and its own SHAP values
        col_idx = IV_COLS.index(var)
        sign = np.corrcoef(X[:, col_idx], shap_values[:, col_idx])[0, 1]
        shap_rows.append({
            "dv": dv_name, "variable": var, "mean_abs_shap": round(float(sv), 4),
            "direction": "positive" if sign > 0 else "negative",
        })

    print(f"  top 3 by SHAP: {sorted(zip(IV_COLS, mean_abs_shap), key=lambda kv: -kv[1])[:3]}")

pd.DataFrame(importance_rows).to_csv(f"{OUT_DIR}/rf_feature_importance.csv", index=False)
pd.DataFrame(shap_rows).to_csv(f"{OUT_DIR}/rf_shap_summary.csv", index=False)
print(f"\nSaved -> {OUT_DIR}/rf_feature_importance.csv")
print(f"Saved -> {OUT_DIR}/rf_shap_summary.csv")
