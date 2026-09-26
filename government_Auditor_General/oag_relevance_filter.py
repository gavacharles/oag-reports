import re

import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/government_Auditor_General"
SRC = f"{BASE}/oag_infrastructure_sentence_corpus_2017_2025_FULLTEXT.csv"

df = pd.read_csv(SRC)
if "construction_relevant" in df.columns:
    df = df.drop(columns=["construction_relevant"])

CONSTRUCTION_CONTRACT_TERMS = [
    r"contractor", r"liquidated\s+damages", r"defects\s+liability", r"extension\s+of\s+time",
    r"bill\s+of\s+quantities", r"practical\s+completion", r"site\s+handover", r"civil\s+works",
    r"\bworks\b", r"certificate\s+of\s+completion", r"retention\s+money", r"performance\s+bond",
    r"site\s+possession", r"variation\s+order",
]
STRONG_TERMS = [
    r"road", r"bridge", r"highway", r"expressway", r"causeway", r"culvert", r"drainage",
    r"construction", r"infrastructure", r"water\s+supply", r"sewerage", r"sanitation", r"borehole",
    r"rail", r"railway", r"energy", r"electricity", r"transmission\s+line", r"power\s+line",
    r"distribution\s+line", r"substation", r"\bgrid\b", r"\bdam\b", r"hydro", r"hospital",
    r"health\s*cent", r"school", r"housing", r"stadium", r"airport", r"building",
    r"wayleave", r"way\s*leave", r"right\s+of\s+way", r"land\s+acquisition",
]
INFRA_AGENCY_RE = re.compile(
    r"UNRA|National Roads Authority|National Water and Sewerage|NWSC|"
    r"Uganda Electricity|UEGCL|UETCL|Umeme|Ministry of Works|MoWT|Kampala Capital City|KCCA|"
    r"Rural Electrification|\bREA\b|Uganda National Roads",
    re.I,
)
strong_re = re.compile(r"\b(" + "|".join(STRONG_TERMS) + r")", re.I)
contract_re = re.compile("|".join(CONSTRUCTION_CONTRACT_TERMS), re.I)

s = df["sentence"].astype(str)
has_strong = s.apply(lambda x: bool(strong_re.search(x)))
has_agency = s.apply(lambda x: bool(INFRA_AGENCY_RE.search(x))) | df["statutory_body"].fillna("").apply(
    lambda x: bool(INFRA_AGENCY_RE.search(x))
)
has_contract = s.apply(lambda x: bool(contract_re.search(x)))
relevant = has_strong | has_agency | has_contract

print(f"has_strong={has_strong.sum()}  has_agency={has_agency.sum()}  has_contract={has_contract.sum()}")
print(f"construction-relevant (union): {relevant.sum()} / {len(df)} ({100*relevant.sum()/len(df):.1f}%)")
print()
print(df.loc[relevant, "primary_driver"].value_counts())

df["construction_relevant"] = relevant
df.to_csv(SRC, index=False)

CLEAN_OUT = f"{BASE}/oag_infrastructure_sentence_corpus_2017_2025_FINAL.csv"
df.loc[relevant].reset_index(drop=True).to_csv(CLEAN_OUT, index=False)
print(f"\nSaved full corpus (with construction_relevant flag) -> {SRC}")
print(f"Saved filtered final corpus -> {CLEAN_OUT}")

print("\n=== still-excluded cost_overrun rows (sanity check) ===")
for x in df.loc[(df["primary_driver"] == "cost_overrun") & ~relevant, "sentence"]:
    print("-", x[:170])
