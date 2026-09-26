"""
Build the year x district panel needed for space-time analysis: for each
audit year 2017-2025 and each district, how many distinct projects had a
finding mentioning that year. A project mentioned across several years
(e.g. audited repeatedly because a dispute persisted) counts in each of
those years -- this deliberately captures "was this district's dispute
picture active in year Y," not "was a new project first observed in Y."

Honest caveat up front: with only 261 district-assigned projects spread
across 9 years and 135 districts, most district-year cells will be zero.
Annual Getis-Ord Gi* on this panel is illustrative of the space-time
*pattern*, not a high-powered test in any single year -- said plainly in
the write-up, not just here.
"""
import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
PROJECTS = f"{BASE}/05_covariates/project_level_with_covariates.csv"
OUT = f"{BASE}/09_space_time/annual_district_counts.csv"

YEARS = list(range(2017, 2026))

df = pd.read_csv(PROJECTS)
df = df[df["district_final"].notna()].copy()

rows = []
for _, r in df.iterrows():
    dist_list = [d.strip() for d in str(r["district_final"]).split(";")]
    years_here = [int(y) for y in str(r["years_mentioned"]).split(";") if y.strip().isdigit()]
    years_here = [y for y in years_here if y in YEARS]
    for dist in dist_list:
        for yr in years_here:
            rows.append({"district": dist, "year": yr})

panel = pd.DataFrame(rows)
counts = panel.groupby(["district", "year"]).size().reset_index(name="n_projects")

# full district x year grid (including zeros) -- need the district list
districts_all = pd.read_csv(f"{BASE}/06_esda/district_driver_counts.csv")["district"].unique()
full_index = pd.MultiIndex.from_product([districts_all, YEARS], names=["district", "year"])
full = pd.DataFrame(index=full_index).reset_index()
full = full.merge(counts, on=["district", "year"], how="left")
full["n_projects"] = full["n_projects"].fillna(0).astype(int)

full.to_csv(OUT, index=False)
print(f"Saved -> {OUT}")
print(f"{len(districts_all)} districts x {len(YEARS)} years = {len(full)} rows")
print("\nnon-zero cells per year:")
print(full[full["n_projects"] > 0].groupby("year").size())
