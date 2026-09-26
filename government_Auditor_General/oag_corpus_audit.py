"""
Data-quality audit and cleaning of the OAG infrastructure sentence corpus.

Finding: the corpus mixes genuine audit-finding sentences with document
front-matter noise (table-of-contents dot-leaders, table/figure captions,
glossary/abbreviations-list text) that was swept in because the PDF-to-text
extraction did not strip front-matter/back-matter before sentence splitting
and keyword classification. This script quantifies and removes that noise,
and reports the effect on category counts (the outcome variable the spatial
paper's project-level dispute-driver classification depends on).
"""
import re

import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/government_Auditor_General"
SRC = f"{BASE}/oag_infrastructure_sentence_corpus_2017_2025_expanded.csv"

df = pd.read_csv(SRC)
s = df["sentence"].fillna("")

FRONTMATTER_PATTERNS = {
    "toc_dot_leader": r"\.{4,}",  # "..........." leaders connecting a heading to a page number
    "abbrev_glossary_header": r"ABBREVIATION|ACRONYM|GLOSSARY OF TERMS|LIST OF TABLES|LIST OF FIGURES|TABLE OF CONTENTS",
    "table_caption": r"^\s*\d{0,4}\s*Table\s+\d+\s*[:.]",       # "Table 44:" or "247 Table 44:"
    "figure_caption": r"^\s*\d{0,4}\s*Figure\s+\d+\s*[:.]",
    "section_header_with_pageref": r"^\s*\d{1,4}\s+[A-Z][a-zA-Z\s]{3,60}\.{2,}\s*\d*\s*$",  # "246 5.4.3 Inspection ...."
}

masks = {name: s.str.contains(pat, regex=True, case=False) for name, pat in FRONTMATTER_PATTERNS.items()}
flag = pd.concat(masks.values(), axis=1).any(axis=1)

print("=== Front-matter contamination audit ===")
for name, m in masks.items():
    print(f"  {name:28s} {m.sum():4d} rows ({100*m.sum()/len(df):.1f}%)")
print(f"  {'ANY PATTERN':28s} {flag.sum():4d} rows ({100*flag.sum()/len(df):.1f}%) of {len(df)} total")

print("\n=== driver_label distribution among flagged (contaminated) rows ===")
print(df.loc[flag, "driver_label"].value_counts())

print("\n=== BEFORE cleaning: full driver_label distribution ===")
before = df["driver_label"].value_counts()
print(before)

clean = df.loc[~flag].reset_index(drop=True)
print(f"\n=== AFTER cleaning: {len(clean)} rows remain (removed {flag.sum()}) ===")
after = clean["driver_label"].value_counts()
print(after)

print("\n=== Change in substantive (non-'other') category counts ===")
compare = pd.DataFrame({"before": before, "after": after}).fillna(0).astype(int)
compare["removed"] = compare["before"] - compare["after"]
compare["pct_removed"] = (100 * compare["removed"] / compare["before"]).round(1)
print(compare[compare.index != "other"].sort_values("removed", ascending=False))

OUT = f"{BASE}/oag_infrastructure_sentence_corpus_2017_2025_CLEANED.csv"
clean.to_csv(OUT, index=False)
print(f"\nSaved cleaned corpus -> {OUT}")

removed_rows = df.loc[flag, ["year", "sentence", "driver_label"]]
removed_rows.to_csv(f"{BASE}/oag_corpus_frontmatter_removed_audit.csv", index=False)
print(f"Saved removed-rows audit trail -> {BASE}/oag_corpus_frontmatter_removed_audit.csv")
