"""
Join district-level covariates onto the project dataset:
- Population 2022 (OCHA COD-PS)
- Rurality / dependency ratio (HeiGIT/HOT risk-assessment vulnerability layer)
- Healthcare/education access bands (HOT access layer)
- Rural Access Index -- RAI, % of rural population within 2km of an
  all-season road (HOT rai layer) -- this is the standard World Bank/RAI
  remoteness measure and the most direct operationalisation of the
  "remoteness predicts land/delay claims" hypothesis in the research design.

Sources are all real, cited, district(ADM2)-level, downloaded this session
(not fabricated): OCHA COD-PS 2022 projections, and HeiGIT/Humanitarian
OpenStreetMap Team's risk-assessment indicator layers (both distributed via
HDX). Poverty-specific figures (UBOS 2024 census, parish-level) are NOT yet
joined -- that dataset is only published as a PDF/report table, not a
machine-readable file, and needs a manual transcription pass; flagged in
the write-up.
"""
import pandas as pd
import geopandas as gpd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/05_covariates"
DISTRICTS = f"{BASE}/boundaries/uga_admin2.geojson"
PROJECTS = f"{BASE}/project_level_with_covariates.csv"
OUT = f"{BASE}/project_level_with_covariates.csv"

districts = gpd.read_file(DISTRICTS)[["adm2_name", "adm2_pcode"]].rename(columns={"adm2_name": "district_final"})

pop = pd.read_csv("/tmp/uga_admpop_adm2.csv")[["ADM2_PCODE", "T_TL", "F_TL", "M_TL"]].rename(
    columns={"ADM2_PCODE": "adm2_pcode", "T_TL": "district_population_2022", "F_TL": "district_pop_female_2022", "M_TL": "district_pop_male_2022"}
)

vuln = pd.read_csv("/tmp/uga_vulnerability.csv")[
    ["ADM2_PCODE", "dependency_ratio", "rural_pop_perc"]
].rename(columns={"ADM2_PCODE": "adm2_pcode"})

access = pd.read_csv("/tmp/uga_access.csv")[
    ["ADM2_PCODE", "access_pop_hospitals_1h", "access_pop_primary_healthcare_1h", "access_pop_education_10km"]
].rename(columns={"ADM2_PCODE": "adm2_pcode"})

rai = pd.read_csv("/tmp/uga_rai.csv")[["ADM2_PCODE", "RAI_total_pop"]].rename(
    columns={"ADM2_PCODE": "adm2_pcode", "RAI_total_pop": "rural_access_index_pct"}
)

# also compute an "access share" from raw counts (access_pop_X / district_population)
merged_district = districts.merge(pop, on="adm2_pcode", how="left") \
    .merge(vuln, on="adm2_pcode", how="left") \
    .merge(access, on="adm2_pcode", how="left") \
    .merge(rai, on="adm2_pcode", how="left")
merged_district["pct_pop_1h_from_hospital"] = (
    100 * merged_district["access_pop_hospitals_1h"] / merged_district["district_population_2022"]
).round(1)
merged_district = merged_district.drop(columns=["access_pop_hospitals_1h"])

print(f"district covariate table: {len(merged_district)} districts, columns: {merged_district.columns.tolist()}")

proj = pd.read_csv(PROJECTS)
before_cols = set(proj.columns)
result = proj.merge(merged_district, on="district_final", how="left", suffixes=("", "_distjoin"))
new_cols = [c for c in result.columns if c not in before_cols]
print(f"\njoined columns: {new_cols}")
print(f"projects with district covariates: {result['district_population_2022'].notna().sum()} / {len(result)}")

missing = result[result["district_final"].notna() & result["district_population_2022"].isna()]
if len(missing):
    print(f"\n{len(missing)} projects have a district_final that didn't match the covariate table (name mismatch) -- worth reconciling:")
    print(missing[["project_name", "district_final"]].drop_duplicates().to_string())

result.to_csv(OUT, index=False)
print(f"\nSaved -> {OUT}")
