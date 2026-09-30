"""
Does media volume on infrastructure disputes move with -- or ahead of, or
behind -- the OAG's annual reporting cycle on the same subject?

Important asymmetry to keep straight, stated up front: the OAG "year" for a
sentence is the calendar year of the REPORT FILE it comes from (the report's
own cover year, close to its Parliament-tabling date), and OAG reports mostly
narrate audit findings from the fiscal year(s) preceding that. Observer's
"year" is the actual publication date of the news article -- much closer to
real time. So the two series are not measuring the same kind of date, and a
naive same-year correlation conflates "did media and audits agree in volume
this calendar year" with the more interesting "does media coverage precede
the audit report that later covers the same ground." This script reports
both the raw annual series and a simple lag check (does shifting Observer's
series by -1 year improve alignment with OAG's), with the sample size
(6 usable OAG years) stated plainly as too small for a confident answer --
this is a descriptive first look, not a powered hypothesis test.

Two OAG years are structurally anomalous and excluded from the correlation
(though shown in the table): 2020 (a strategic-planning document, not an
annual audit report -- only 15 sentences) and 2021 (a COVID-19 thematic
report, not the standard annual audit -- only 5 sentences). 2017 has zero
sentences in the analysis corpus (no cached report content survived
extraction for that year; see Section 3.1's caveat on report availability).
"""
import pandas as pd
from scipy.stats import spearmanr, pearsonr

PAPER1_BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
OAG_CORPUS = f"{PAPER1_BASE}/03_relevance_filter/oag_infrastructure_sentence_corpus_2017_2025_FINAL.csv"
OBSERVER_SENTENCES = "/Users/charlesgava/Documents/Projects /The Observer/paper2_online_discourse/outputs_observer_full_corpus/sentences_classified.csv"
OUT_DIR = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_media_vs_audit_discourse/01_framing_geography_timing"

oag = pd.read_csv(OAG_CORPUS, usecols=["year"])
oag_annual = oag.groupby("year").size().rename("oag_n_sentences")

obs = pd.read_csv(OBSERVER_SENTENCES, usecols=["publication_date"])
obs["year"] = pd.to_datetime(obs["publication_date"], errors="coerce").dt.year
obs_annual = obs.groupby("year").size().rename("observer_n_sentences")

panel = pd.concat([oag_annual, obs_annual], axis=1).sort_index()
panel["oag_report_type"] = "standard annual audit"
panel.loc[2020, "oag_report_type"] = "strategic-planning doc (non-standard)"
panel.loc[2021, "oag_report_type"] = "COVID-19 thematic report (non-standard)"
if 2017 in panel.index:
    panel.loc[2017, "oag_report_type"] = "no content in analysis corpus"
print("=== Full annual panel (all years present in either source) ===")
print(panel.to_string())
panel.to_csv(f"{OUT_DIR}/annual_volume_panel.csv")

# usable years for correlation: OAG has a standard annual report AND Observer
# has data that same year
usable = panel[(panel["oag_report_type"] == "standard annual audit") & panel["oag_n_sentences"].notna() & panel["observer_n_sentences"].notna()]
print(f"\nUsable years for correlation (standard OAG report + Observer data present): {list(usable.index)}  (n={len(usable)})")

# contemporaneous: OAG(Y) vs Observer(Y)
r0, p0 = pearsonr(usable["oag_n_sentences"], usable["observer_n_sentences"])
rho0, ps0 = spearmanr(usable["oag_n_sentences"], usable["observer_n_sentences"])
print(f"\nContemporaneous  OAG(Y) vs Observer(Y):    Pearson r={r0:.3f} (p={p0:.3f}), Spearman rho={rho0:.3f} (p={ps0:.3f})")

# lag: OAG(Y) vs Observer(Y-1) -- "did media coverage the year before line up with
# the audit report's volume the year it was released"
lagged = usable.copy()
lagged["observer_n_sentences_lag1"] = [obs_annual.get(y - 1, float("nan")) for y in usable.index]
lagged = lagged.dropna(subset=["observer_n_sentences_lag1"])
r1, p1 = pearsonr(lagged["oag_n_sentences"], lagged["observer_n_sentences_lag1"])
rho1, ps1 = spearmanr(lagged["oag_n_sentences"], lagged["observer_n_sentences_lag1"])
print(f"Lagged  OAG(Y) vs Observer(Y-1):           Pearson r={r1:.3f} (p={p1:.3f}), Spearman rho={rho1:.3f} (p={ps1:.3f})")
print(f"(n={len(lagged)} for both checks -- too small for a confident conclusion either way; reported as descriptive)")

lagged.to_csv(f"{OUT_DIR}/lagged_volume_check.csv")

with open(f"{OUT_DIR}/volume_lead_lag_results.txt", "w") as f:
    f.write(f"usable_years: {list(usable.index)}\n")
    f.write(f"contemporaneous: pearson_r={r0:.3f} p={p0:.3f} spearman_rho={rho0:.3f} p={ps0:.3f}\n")
    f.write(f"lag1 (OAG(Y) vs Observer(Y-1)): pearson_r={r1:.3f} p={p1:.3f} spearman_rho={rho1:.3f} p={ps1:.3f}\n")

print(f"\nSaved -> {OUT_DIR}/annual_volume_panel.csv")
print(f"Saved -> {OUT_DIR}/lagged_volume_check.csv")
