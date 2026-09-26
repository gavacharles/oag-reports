"""
Step 1 of the gold-standard validation of the OAG multi-label driver
classifier (DRIVER_PATTERNS in 02_full_reextraction/oag_full_reextraction.py).

Draws a stratified sample from the analysis corpus (792 sentences), stratified
by `primary_driver` (used ONLY for sampling balance, not as ground truth),
up to 50 per category (fewer if the category has under 50 total). Seed=42
for reproducibility.

Saves a BLINDED sample (no classifier labels) for independent AI-assisted
coding in gold_labels.csv (Step 3). The original dataframe index is carried
as `orig_index` so gold_labels can be joined back to the FINAL.csv row
(and therefore to all_drivers) at scoring time (Step 4) without the coder
ever seeing the classifier's labels during coding.
"""
import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/03_relevance_filter"
SRC = f"{BASE}/oag_infrastructure_sentence_corpus_2017_2025_FINAL.csv"
OUT = f"{BASE}/gold_standard/sample_blinded.csv"
OUT_KEY = f"{BASE}/gold_standard/sample_key_DO_NOT_USE_WHILE_CODING.csv"  # keeps orig_index + labels for later join only

SEED = 42
N_PER_CATEGORY = 50

df = pd.read_csv(SRC)
df = df.reset_index(drop=False).rename(columns={"index": "orig_index"})

samples = []
for cat, group in df.groupby("primary_driver"):
    n = min(N_PER_CATEGORY, len(group))
    s = group.sample(n=n, random_state=SEED)
    samples.append(s)

sample_df = pd.concat(samples, ignore_index=True)
sample_df = sample_df.sample(frac=1, random_state=SEED).reset_index(drop=True)  # shuffle so category order isn't visible
sample_df.insert(0, "sample_id", [f"S{i+1:04d}" for i in range(len(sample_df))])

print(f"Total sampled: {len(sample_df)}")
print(sample_df["primary_driver"].value_counts())

# Blinded file for coding: no classifier labels visible.
blinded = sample_df[["sample_id", "year", "sentence"]].copy()
blinded.to_csv(OUT, index=False)
print(f"\nBlinded sample saved -> {OUT}")

# Key file (kept separately, NOT to be opened while coding) for the Step 4 join.
key = sample_df[["sample_id", "orig_index", "year", "sentence", "primary_driver", "all_drivers", "n_drivers_matched"]].copy()
key.to_csv(OUT_KEY, index=False)
print(f"Key (for scoring only) saved -> {OUT_KEY}")
