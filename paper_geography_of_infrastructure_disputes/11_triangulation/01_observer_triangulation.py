"""
Triangulation check: does the OAG audit-derived dispute geography agree
with the geography implicit in an independent data source -- The
Observer newspaper's dispute-relevant article corpus (2016-2025, from
the companion newspaper-text-mining study), which was built from
entirely different source documents (news articles, not audit reports),
by a different extraction pipeline, with no shared authorship between
the two corpora's classification steps beyond the same research team?

If the two sources agree on where disputes concentrate, that is real
external validation the paper's own audit-coverage caveat cannot supply
internally. If they diverge, that is itself informative about what OAG
audits vs. what newspapers report.

Important scope limitation, stated up front: the Observer location
gazetteer covers only 29 curated place names nationally (not all 135
districts), 7 of which are cross-border/sub-regional and excluded here
as not mapping to a single Uganda district. This is a real but narrow
triangulation on the subset of well-known places both sources happen to
cover, not a full national comparison.
"""
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
OBSERVER_LOC = "/Users/charlesgava/Documents/Projects /The Observer/paper2_online_discourse/outputs_observer_full_corpus/newspaper_only_analysis/location_mentions_top.csv"
OAG_COUNTS = f"{BASE}/06_esda/district_driver_counts.csv"
OUT_DIR = f"{BASE}/11_triangulation"

# place -> district mapping, built by direct knowledge of Uganda administrative
# geography (documented per-row below); excluded rows are sub-regional or
# cross-border and do not map to one district.
PLACE_TO_DISTRICT = {
    "Kampala": "Kampala",
    "Nakawa": "Kampala",          # division of Kampala city
    "Nakivubo": "Kampala",        # stadium/channel within Kampala city
    "Entebbe": "Wakiso",          # Entebbe town, Wakiso District
    "Lubowa": "Wakiso",
    "Wakiso": "Wakiso",
    "Namboole": "Wakiso",         # Mandela National Stadium, Wakiso
    "Mukono": "Mukono",
    "Jinja": "Jinja",
    "Bujagali": "Jinja",          # Bujagali Falls/dam, Jinja District
    "Mbale": "Mbale",
    "Soroti": "Soroti",
    "Tororo": "Tororo",
    "Gulu": "Gulu",
    "Kitgum": "Kitgum",
    "Arua": "Arua",
    "Lira": "Lira",
    "Hoima": "Hoima",
    "Kabale": "Kabale",
    "Kabaale": "Hoima",           # Kabaale (Hoima) oil-refinery/airport site -- NOT Kabale district; same
                                    # disambiguation applied in this paper's own OAG geocoding (Section 3.2)
    "Mubende": "Mubende",
    "Isimba": "Kayunga",          # Isimba dam, consistent with this paper's own project-level geocoding
    "Karuma": "Kiryandongo",      # Karuma Falls/dam site
    # excluded as sub-regional / cross-border, not a single district:
    "Karamoja": None, "Bunyoro": None, "Nile": None,
    "South Sudan": None, "DRC": None, "Kenya": None, "Tanzania": None,
}

obs = pd.read_csv(OBSERVER_LOC)
obs["district"] = obs["location"].map(PLACE_TO_DISTRICT)
excluded = obs[obs["district"].isna()]
print(f"Observer locations excluded (sub-regional/cross-border): {excluded['location'].tolist()}")
obs = obs.dropna(subset=["district"])
obs_district = obs.groupby("district")["article_mentions"].sum().reset_index()
obs_district = obs_district.rename(columns={"article_mentions": "observer_article_mentions"})
print(f"\nObserver: {len(obs_district)} distinct districts after mapping "
      f"(from {obs['location'].nunique()} place names)")

oag = pd.read_csv(OAG_COUNTS)[["district", "n_projects"]]

merged = obs_district.merge(oag, on="district", how="inner")
print(f"\nDistricts present in BOTH sources: {len(merged)}")
print(merged.sort_values("observer_article_mentions", ascending=False).to_string(index=False))

rho, pval = spearmanr(merged["observer_article_mentions"], merged["n_projects"])
print(f"\nSpearman rank correlation (Observer article mentions vs. OAG project count): "
      f"rho={rho:.3f}, p={pval:.4f}, n={len(merged)}")

merged.to_csv(f"{OUT_DIR}/triangulation_comparison.csv", index=False)

# scatter plot
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(merged["observer_article_mentions"], merged["n_projects"], s=60, color="#2a78d6", alpha=0.85, edgecolor="white")
for _, r in merged.iterrows():
    ax.annotate(r["district"], (r["observer_article_mentions"], r["n_projects"]),
                fontsize=8, xytext=(4, 4), textcoords="offset points", color="#52514e")
ax.set_xlabel("Observer newspaper: dispute-relevant article mentions (2016-2025)")
ax.set_ylabel("OAG audit: geocoded project count (2017-2025)")
ax.set_title(f"District-level triangulation, two independent sources\n"
             f"Spearman ρ = {rho:.3f} (p = {pval:.4f}, n = {len(merged)} districts)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/figure_triangulation.png", dpi=200, bbox_inches="tight")
print(f"\nSaved -> {OUT_DIR}/figure_triangulation.png")
print(f"Saved -> {OUT_DIR}/triangulation_comparison.csv")
