"""
RQ2, properly tested: did road-sector (UNRA's domain) disputes shift
differently around the Government of Uganda's 2021 rationalisation
decision (fold UNRA into MoWT; legally implemented Nov 2024) than
non-road-sector disputes did over the same window? A simple before/after
comparison confounds "changed because of the transition" with "changed
because everything changed" (COVID recovery, general audit-volume
growth, etc.); comparing road against non-road over the identical window
is the difference-in-differences logic that isolates whatever is
road-specific.

Break point: 2021 (the policy announcement year, which is what actually
falls inside this study's 2017-2025 window with usable data on both
sides -- the legal dissolution didn't happen until Nov 2024, right at
the tail of the window, leaving almost no "after" data if that date were
used instead). This is stated explicitly rather than left for a reader
to reconstruct.
"""
import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
PROJECTS = f"{BASE}/05_covariates/project_level_with_covariates.csv"
OUT_DIR = f"{BASE}/11_triangulation"

BREAK_YEAR = 2021
PRE_YEARS = list(range(2017, 2021))   # 2017-2020, 4 years
POST_YEARS = list(range(2021, 2026))  # 2021-2025, 5 years

df = pd.read_csv(PROJECTS)
df["is_road"] = df["project_type"] == "road"

# project -> year panel (one row per project-year mention)
rows = []
for _, r in df.iterrows():
    years = [int(y) for y in str(r["years_mentioned"]).split(";") if y.strip().isdigit()]
    for y in years:
        if y in PRE_YEARS or y in POST_YEARS:
            rows.append({
                "project_name": r["project_name"], "year": y, "is_road": r["is_road"],
                "distance_to_kampala_km": r["distance_to_kampala_km"],
                "period": "pre" if y in PRE_YEARS else "post",
            })
panel = pd.DataFrame(rows)
print(f"project-year mentions in window: {len(panel)} ({panel['is_road'].sum()} road, {(~panel['is_road']).sum()} non-road)")

# normalized rate: mentions per year, by sector and period
summary = panel.groupby(["is_road", "period"]).size().reset_index(name="n_mentions")
summary["n_years"] = summary["period"].map({"pre": len(PRE_YEARS), "post": len(POST_YEARS)})
summary["rate_per_year"] = summary["n_mentions"] / summary["n_years"]
print("\n", summary.to_string(index=False))

def rate(is_road, period):
    row = summary[(summary["is_road"] == is_road) & (summary["period"] == period)]
    return row["rate_per_year"].iloc[0] if len(row) else 0.0

road_pre, road_post = rate(True, "pre"), rate(True, "post")
nonroad_pre, nonroad_post = rate(False, "pre"), rate(False, "post")
road_change = road_post - road_pre
nonroad_change = nonroad_post - nonroad_pre
did = road_change - nonroad_change

print(f"\nRoad:     pre={road_pre:.2f}/yr -> post={road_post:.2f}/yr  (change {road_change:+.2f})")
print(f"Non-road: pre={nonroad_pre:.2f}/yr -> post={nonroad_post:.2f}/yr  (change {nonroad_change:+.2f})")
print(f"Difference-in-differences (road change minus non-road change): {did:+.2f} mentions/year")

# geographic angle: does road-dispute distance-to-Kampala shift pre->post,
# relative to non-road?
dist_summary = panel.dropna(subset=["distance_to_kampala_km"]).groupby(["is_road", "period"])["distance_to_kampala_km"].agg(["mean", "median", "count"]).reset_index()
print("\nDistance-to-Kampala by sector and period:")
print(dist_summary.to_string(index=False))

def dist_val(is_road, period, col="mean"):
    row = dist_summary[(dist_summary["is_road"] == is_road) & (dist_summary["period"] == period)]
    return row[col].iloc[0] if len(row) else float("nan")

road_dist_pre, road_dist_post = dist_val(True, "pre"), dist_val(True, "post")
nonroad_dist_pre, nonroad_dist_post = dist_val(False, "pre"), dist_val(False, "post")
print(f"\nRoad distance-to-Kampala:     pre={road_dist_pre:.1f}km -> post={road_dist_post:.1f}km "
      f"(change {road_dist_post-road_dist_pre:+.1f}km)")
print(f"Non-road distance-to-Kampala: pre={nonroad_dist_pre:.1f}km -> post={nonroad_dist_post:.1f}km "
      f"(change {nonroad_dist_post-nonroad_dist_pre:+.1f}km)")

# simple significance check on the rate DiD via a 2x2 chi-square / Poisson-ish test
from scipy.stats import chi2_contingency
table = summary.pivot(index="is_road", columns="period", values="n_mentions").fillna(0)
# use rates scaled to a common denominator (years) for a fair contingency-style check is awkward;
# report raw counts contingency test as a simple, transparent significance probe instead
chi2, p, dof, exp = chi2_contingency(table.values)
print(f"\nChi-square test on the 2x2 (sector x period) raw mention-count table: chi2={chi2:.3f}, p={p:.4f}")

results = {
    "break_year": BREAK_YEAR, "pre_years": PRE_YEARS, "post_years": POST_YEARS,
    "road_rate_pre": round(road_pre, 3), "road_rate_post": round(road_post, 3),
    "nonroad_rate_pre": round(nonroad_pre, 3), "nonroad_rate_post": round(nonroad_post, 3),
    "diff_in_diff": round(did, 3),
    "road_dist_pre_km": round(road_dist_pre, 1), "road_dist_post_km": round(road_dist_post, 1),
    "nonroad_dist_pre_km": round(nonroad_dist_pre, 1), "nonroad_dist_post_km": round(nonroad_dist_post, 1),
    "chi2": round(chi2, 3), "chi2_p": round(p, 4),
}
pd.Series(results).to_csv(f"{OUT_DIR}/unra_mowt_transition_results.csv")
panel.to_csv(f"{OUT_DIR}/unra_mowt_panel.csv", index=False)
print(f"\nSaved -> {OUT_DIR}/unra_mowt_transition_results.csv")
print(f"Saved -> {OUT_DIR}/unra_mowt_panel.csv")
