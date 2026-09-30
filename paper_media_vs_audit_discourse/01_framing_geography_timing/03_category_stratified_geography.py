"""
RQ2 for the second paper: does audit/media agreement on WHERE disputes are
depend on WHICH category you're looking at? Paper 1's Section 5.4 only
tested overall intensity (rho=0.369, p=0.160 across 16 districts, collapsing
to 0.051 excl. Kampala/Wakiso). This extends that -- not repeats it -- to
each of the six dispute categories both classifiers share, reusing the same
disclosed place-to-district gazetteer from 11_triangulation/01_observer_triangulation.py
so the district base is identical and results are directly comparable.

Observer side has no pre-built district x category table (the existing
location_mentions_top.csv is category-blind), so this script builds one:
for each article, (a) find which gazetteer places its title+text mention
(case-sensitive, word-boundary regex -- the same simple approach the
original triangulation used), (b) find which categories its sentences were
classified into (from sentences_classified.csv, joined by url). An article
counts toward a (district, category) cell if it hits both -- i.e. this is
an article-level co-occurrence, not a claim that the category-labelled
sentence and the place-mention are the same sentence. That's a real
granularity limitation, stated plainly below, not hidden.
"""
import re
import pandas as pd
from scipy.stats import spearmanr

PAPER1_BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
OAG_DISTRICT_DRIVERS = f"{PAPER1_BASE}/06_esda/district_driver_counts.csv"
OBS_ARTICLES = "/Users/charlesgava/Documents/Projects /The Observer/paper2_online_discourse/outputs_observer_full_corpus/articles_relevant.csv"
OBS_SENTENCES = "/Users/charlesgava/Documents/Projects /The Observer/paper2_online_discourse/outputs_observer_full_corpus/sentences_classified.csv"
OUT_DIR = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_media_vs_audit_discourse/01_framing_geography_timing"

# identical to 11_triangulation/01_observer_triangulation.py -- same disclosed
# disambiguation, reused rather than redefined, so the district base matches
PLACE_TO_DISTRICT = {
    "Kampala": "Kampala", "Nakawa": "Kampala", "Nakivubo": "Kampala",
    "Entebbe": "Wakiso", "Lubowa": "Wakiso", "Wakiso": "Wakiso", "Namboole": "Wakiso",
    "Mukono": "Mukono", "Jinja": "Jinja", "Bujagali": "Jinja", "Mbale": "Mbale",
    "Soroti": "Soroti", "Tororo": "Tororo", "Gulu": "Gulu", "Kitgum": "Kitgum",
    "Arua": "Arua", "Lira": "Lira", "Hoima": "Hoima", "Kabale": "Kabale",
    "Kabaale": "Hoima", "Mubende": "Mubende", "Isimba": "Kayunga", "Karuma": "Kiryandongo",
}
PLACES = sorted(PLACE_TO_DISTRICT.keys(), key=len, reverse=True)  # longer names first (Kabaale before Kabale-safe)
PLACE_PATTERNS = {p: re.compile(r"\b" + re.escape(p) + r"\b") for p in PLACES}

# OAG category name -> Observer category name (the six that overlap; see
# CATEGORY_FRAMING_WRITEUP.md for the full mapping and the two non-overlapping
# categories on each side)
CATEGORY_MAP = {
    "delay_time_overrun": "delay_time_overrun",
    "land_and_right_of_way": "land_row_dispute",
    "procurement_irregularities": "procurement_irregularity",
    "contract_management": "contract_management_failure",
    "delayed_payments": "payment_financial_dispute",
    "governance_and_controls": "governance_oversight_failure",
}

print("Loading OAG district x category counts...")
oag = pd.read_csv(OAG_DISTRICT_DRIVERS)

print("Loading Observer articles and finding place mentions (title+text, word-boundary match)...")
arts = pd.read_csv(OBS_ARTICLES, usecols=["url", "title", "text"])
arts["full_text"] = arts["title"].fillna("") + " " + arts["text"].fillna("")

def find_districts(text):
    hit_places = [p for p in PLACES if PLACE_PATTERNS[p].search(text)]
    return set(PLACE_TO_DISTRICT[p] for p in hit_places)

arts["districts"] = arts["full_text"].apply(find_districts)
arts_with_place = arts[arts["districts"].map(len) > 0][["url", "districts"]]
print(f"Articles with >=1 gazetteer place mention: {len(arts_with_place)} of {len(arts)}")

print("Loading Observer sentence categories and collapsing to per-article category sets...")
sents = pd.read_csv(OBS_SENTENCES, usecols=["url", "pred_final"])
art_categories = sents.groupby("url")["pred_final"].apply(lambda s: set(s.dropna())).rename("categories")

merged = arts_with_place.merge(art_categories, on="url", how="inner")
print(f"Articles with both a place mention and >=1 classified sentence: {len(merged)}")

# build district x category article-count matrix (article counts once per
# district it mentions, once per category it contains -- co-occurrence, not
# sentence-level joint labeling)
records = []
for _, row in merged.iterrows():
    for d in row["districts"]:
        for c in row["categories"]:
            records.append((d, c))
pair_counts = pd.DataFrame(records, columns=["district", "observer_category"]).value_counts().reset_index(name="article_mentions")

pair_counts.to_csv(f"{OUT_DIR}/observer_district_category_counts.csv", index=False)
print(f"Saved -> {OUT_DIR}/observer_district_category_counts.csv ({len(pair_counts)} district x category cells)")

# per-category Spearman correlation, restricted to the same 16-district base
# the original overall triangulation used (districts present in the Observer
# gazetteer mapping AND in the OAG project data)
BASE_DISTRICTS = sorted(set(PLACE_TO_DISTRICT.values()))
oag_base = oag[oag["district"].isin(BASE_DISTRICTS)].set_index("district")

results = []
for oag_cat, obs_cat in CATEGORY_MAP.items():
    oag_col = oag_base[oag_cat]
    obs_col = pair_counts[pair_counts["observer_category"] == obs_cat].set_index("district")["article_mentions"]
    both = pd.DataFrame({"oag_n": oag_col, "observer_n": obs_col}).reindex(BASE_DISTRICTS).fillna(0)
    n_nonzero_oag = (both["oag_n"] > 0).sum()
    n_nonzero_obs = (both["observer_n"] > 0).sum()
    if both["oag_n"].sum() == 0 or both["observer_n"].sum() == 0:
        rho, p = float("nan"), float("nan")
    else:
        rho, p = spearmanr(both["oag_n"], both["observer_n"])
    results.append({
        "category": oag_cat, "n_districts": len(BASE_DISTRICTS),
        "n_districts_oag_nonzero": n_nonzero_oag, "n_districts_observer_nonzero": n_nonzero_obs,
        "oag_total_n": int(both["oag_n"].sum()), "observer_total_n": int(both["observer_n"].sum()),
        "spearman_rho": round(rho, 3) if rho == rho else None,
        "spearman_p": round(p, 4) if p == p else None,
    })

results_df = pd.DataFrame(results)
print("\n=== Per-category district-level agreement (16-district base) ===")
print(results_df.to_string(index=False))
results_df.to_csv(f"{OUT_DIR}/category_stratified_geography_results.csv", index=False)
print(f"\nSaved -> {OUT_DIR}/category_stratified_geography_results.csv")
