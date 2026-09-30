"""
Does government audit and independent media framing of infrastructure disputes
agree on WHICH KINDS of problems matter, not just WHERE (Section 5.4's
district-level triangulation already answered "where")?

Two independently built, independently classified corpora exist:
- OAG: 792 construction-relevant sentences, 8 dispute-driver categories,
  classifier validated (macro-F1 = 0.627; see paper Section 3.4).
- Observer: 24,237 dispute-relevant sentences, 7 dispute-risk categories,
  classifier also validated (macro-F1 = 0.231 -- much weaker; see that
  project's own gold_standard/ folder).

This script does two things, deliberately kept separate because they carry
different evidentiary weight:
1. RAW category-share comparison -- what each classifier's labels say,
   at face value.
2. PRECISION-CORRECTED comparison -- raw share multiplied by each
   category's own validated precision, to approximate what share of each
   predicted category is actually, on independent reading, about that
   construct. This does NOT redistribute false positives to their true
   category (that would need the full confusion matrix, not just
   precision), so corrected shares do not sum to the raw total -- they
   are a deflation, not a reallocation, and are reported as such.

Category mapping (six overlap; two are OAG-only; one is Observer-only --
the mismatch itself is a finding, not a gap to paper over):
  OAG                          <-> Observer
  delay_time_overrun           <-> delay_time_overrun
  land_and_right_of_way        <-> land_row_dispute
  procurement_irregularities   <-> procurement_irregularity
  contract_management          <-> contract_management_failure
  delayed_payments             <-> payment_financial_dispute
  governance_and_controls      <-> governance_oversight_failure
  cost_overrun                 <-> (none)
  claims_and_disputes          <-> (none)
  (none)                       <-> quality_technical_defect
"""
import pandas as pd

PAPER1_BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
OAG_CORPUS = f"{PAPER1_BASE}/03_relevance_filter/oag_infrastructure_sentence_corpus_2017_2025_FINAL.csv"
OUT_DIR = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_media_vs_audit_discourse/01_framing_geography_timing"

# -- OAG side: raw primary_driver counts + this paper's own validated precision (Table 3) --
oag_raw = {
    "procurement_irregularities": 202, "contract_management": 139, "delay_time_overrun": 135,
    "delayed_payments": 98, "land_and_right_of_way": 90, "governance_and_controls": 66,
    "claims_and_disputes": 47, "cost_overrun": 15,
}
oag_precision = {
    "delay_time_overrun": 1.000, "cost_overrun": 0.867, "claims_and_disputes": 0.735,
    "land_and_right_of_way": 0.925, "contract_management": 0.717, "delayed_payments": 0.391,
    "governance_and_controls": 0.333, "procurement_irregularities": 0.724,
}
oag_total = sum(oag_raw.values())
assert oag_total == 792, oag_total

# -- Observer side: raw pred_final counts (table_category_distribution.csv) + its own
#    gold-standard precision (validation_results_table.csv) --
obs_raw = {
    "land_row_dispute": 15173, "delay_time_overrun": 3514, "procurement_irregularity": 1555,
    "quality_technical_defect": 1475, "governance_oversight_failure": 1045,
    "contract_management_failure": 898, "payment_financial_dispute": 577,
}
obs_precision = {
    "contract_management_failure": 0.17, "delay_time_overrun": 0.18, "governance_oversight_failure": 0.31,
    "land_row_dispute": 0.08, "payment_financial_dispute": 0.34, "procurement_irregularity": 0.16,
    "quality_technical_defect": 0.20,
}
obs_total = sum(obs_raw.values())
assert obs_total == 24237, obs_total

MAP = {
    "delay_time_overrun": "delay_time_overrun",
    "land_and_right_of_way": "land_row_dispute",
    "procurement_irregularities": "procurement_irregularity",
    "contract_management": "contract_management_failure",
    "delayed_payments": "payment_financial_dispute",
    "governance_and_controls": "governance_oversight_failure",
}

rows = []
for oag_cat, obs_cat in MAP.items():
    oag_n, oag_p = oag_raw[oag_cat], oag_precision[oag_cat]
    obs_n, obs_p = obs_raw[obs_cat], obs_precision[obs_cat]
    rows.append({
        "oag_category": oag_cat, "observer_category": obs_cat,
        "oag_raw_n": oag_n, "oag_raw_share_pct": round(100 * oag_n / oag_total, 1),
        "oag_precision": oag_p, "oag_corrected_n": round(oag_n * oag_p, 1),
        "observer_raw_n": obs_n, "observer_raw_share_pct": round(100 * obs_n / obs_total, 2),
        "observer_precision": obs_p, "observer_corrected_n": round(obs_n * obs_p, 1),
    })
overlap = pd.DataFrame(rows)

# corrected shares, computed within the corrected total of *only the six overlapping
# categories* on each side (excludes each source's unique categories, so the two
# corrected-share columns are comparable to each other)
overlap["oag_corrected_share_pct"] = round(100 * overlap["oag_corrected_n"] / overlap["oag_corrected_n"].sum(), 1)
overlap["observer_corrected_share_pct"] = round(100 * overlap["observer_corrected_n"] / overlap["observer_corrected_n"].sum(), 1)

print("=== Six overlapping categories: raw vs. precision-corrected shares ===")
print(overlap[["oag_category", "oag_raw_share_pct", "oag_corrected_share_pct",
                "observer_raw_share_pct", "observer_corrected_share_pct"]].to_string(index=False))

overlap.to_csv(f"{OUT_DIR}/category_framing_comparison.csv", index=False)

# each source's unique categories, for the record
unique_oag = pd.DataFrame([
    {"category": "cost_overrun", "raw_n": oag_raw["cost_overrun"], "raw_share_pct": round(100*oag_raw["cost_overrun"]/oag_total, 1), "precision": oag_precision["cost_overrun"]},
    {"category": "claims_and_disputes", "raw_n": oag_raw["claims_and_disputes"], "raw_share_pct": round(100*oag_raw["claims_and_disputes"]/oag_total, 1), "precision": oag_precision["claims_and_disputes"]},
])
unique_obs = pd.DataFrame([
    {"category": "quality_technical_defect", "raw_n": obs_raw["quality_technical_defect"], "raw_share_pct": round(100*obs_raw["quality_technical_defect"]/obs_total, 2), "precision": obs_precision["quality_technical_defect"]},
])
print("\n=== OAG-only categories (no Observer counterpart) ===")
print(unique_oag.to_string(index=False))
print("\n=== Observer-only category (no OAG counterpart) ===")
print(unique_obs.to_string(index=False))

unique_oag.to_csv(f"{OUT_DIR}/oag_only_categories.csv", index=False)
unique_obs.to_csv(f"{OUT_DIR}/observer_only_categories.csv", index=False)

# rank comparison: does the RELATIVE ORDERING of the six shared categories agree,
# even if absolute shares don't? (Spearman on ranks is more robust to the very
# different precision levels of the two classifiers than comparing raw magnitudes)
from scipy.stats import spearmanr
rho_raw, p_raw = spearmanr(overlap["oag_raw_share_pct"], overlap["observer_raw_share_pct"])
rho_corr, p_corr = spearmanr(overlap["oag_corrected_share_pct"], overlap["observer_corrected_share_pct"])
print(f"\nSpearman rank correlation across the 6 shared categories:")
print(f"  raw shares:       rho={rho_raw:.3f}, p={p_raw:.4f}")
print(f"  corrected shares: rho={rho_corr:.3f}, p={p_corr:.4f}")

with open(f"{OUT_DIR}/category_rank_correlation.txt", "w") as f:
    f.write(f"raw: rho={rho_raw:.3f}, p={p_raw:.4f}\ncorrected: rho={rho_corr:.3f}, p={p_corr:.4f}\n")

print(f"\nSaved -> {OUT_DIR}/category_framing_comparison.csv")
print(f"Saved -> {OUT_DIR}/oag_only_categories.csv")
print(f"Saved -> {OUT_DIR}/observer_only_categories.csv")
