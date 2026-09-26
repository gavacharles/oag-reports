"""
Step 4 of the gold-standard validation: score the classifier's multi-label
`all_drivers` output against the independent (AI-assisted, single-rater)
gold_labels.csv, joined via sample_id -> orig_index -> the original
FINAL.csv row.

For each of the 8 DRIVER_PATTERNS categories, computes:
    TP = classifier assigned the label AND gold assigned it
    FP = classifier assigned the label but gold did NOT
    FN = gold assigned the label but classifier did NOT
    TN = neither assigned it
    precision = TP / (TP + FP)   [of what the classifier flagged, how much was right]
    recall    = TP / (TP + FN)   [of what should have been flagged, how much was caught]
    F1        = 2PR / (P + R)

Also builds:
  - macro-averaged precision/recall/F1 across the 8 categories
  - an over-assignment / under-assignment summary per category (how many
    sentences the classifier wrongly added a label to (FP) vs wrongly
    missed (FN), and what the classifier's FP labels tend to co-occur with
    in the gold reading -- i.e. which categories get confused for which)

Outputs:
  validation_results.csv    -- one row per category
  validation_summary.json   -- macro averages + sample size + confusion notes
"""
import json
from pathlib import Path

import pandas as pd

BASE = Path("/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/03_relevance_filter/gold_standard")

CATEGORIES = [
    "delay_time_overrun",
    "cost_overrun",
    "claims_and_disputes",
    "land_and_right_of_way",
    "contract_management",
    "delayed_payments",
    "governance_and_controls",
    "procurement_irregularities",
]


def parse_labels(cell) -> set:
    if pd.isna(cell) or str(cell).strip() == "":
        return set()
    return set(str(cell).split("|"))


def main():
    key = pd.read_csv(BASE / "sample_key_DO_NOT_USE_WHILE_CODING.csv")
    gold = pd.read_csv(BASE / "gold_labels.csv")

    df = key.merge(gold, on="sample_id", how="inner", validate="one_to_one")
    assert len(df) == len(key) == len(gold), "join dropped or duplicated rows"

    df["classifier_set"] = df["all_drivers"].apply(parse_labels)
    df["gold_set"] = df["gold_labels"].apply(parse_labels)

    n = len(df)

    rows = []
    # over/under-assignment detail: for FP sentences (classifier said X, gold
    # didn't), which other category(ies) did gold actually assign instead?
    # for FN sentences (gold said X, classifier missed it), what (if
    # anything) did the classifier assign instead?
    confusion = {cat: {"fp_confused_with": {}, "fn_confused_with": {}} for cat in CATEGORIES}

    for cat in CATEGORIES:
        tp = fp = fn = tn = 0
        for _, r in df.iterrows():
            c_has = cat in r["classifier_set"]
            g_has = cat in r["gold_set"]
            if c_has and g_has:
                tp += 1
            elif c_has and not g_has:
                fp += 1
                for other in r["gold_set"]:
                    confusion[cat]["fp_confused_with"][other] = confusion[cat]["fp_confused_with"].get(other, 0) + 1
                if not r["gold_set"]:
                    confusion[cat]["fp_confused_with"]["(nothing_gold)"] = confusion[cat]["fp_confused_with"].get("(nothing_gold)", 0) + 1
            elif (not c_has) and g_has:
                fn += 1
                for other in r["classifier_set"]:
                    confusion[cat]["fn_confused_with"][other] = confusion[cat]["fn_confused_with"].get(other, 0) + 1
                if not r["classifier_set"]:
                    confusion[cat]["fn_confused_with"]["(nothing_classifier)"] = confusion[cat]["fn_confused_with"].get("(nothing_classifier)", 0) + 1
            else:
                tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
        recall = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 and not pd.isna(precision) and not pd.isna(recall) else float("nan")

        n_gold_positive = tp + fn
        n_classifier_positive = tp + fp

        rows.append({
            "category": cat,
            "n_gold_positive": n_gold_positive,
            "n_classifier_positive": n_classifier_positive,
            "TP": tp,
            "FP": fp,
            "FN": fn,
            "TN": tn,
            "precision": round(precision, 4) if not pd.isna(precision) else None,
            "recall": round(recall, 4) if not pd.isna(recall) else None,
            "F1": round(f1, 4) if not pd.isna(f1) else None,
        })

    results = pd.DataFrame(rows)
    results.to_csv(BASE / "validation_results.csv", index=False)

    valid_p = results["precision"].dropna()
    valid_r = results["recall"].dropna()
    valid_f1 = results["F1"].dropna()

    macro_precision = valid_p.mean()
    macro_recall = valid_r.mean()
    macro_f1 = valid_f1.mean()

    # micro (pooled) averages, for reference alongside macro
    total_tp = results["TP"].sum()
    total_fp = results["FP"].sum()
    total_fn = results["FN"].sum()
    micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else None
    micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else None
    micro_f1 = (2 * micro_precision * micro_recall / (micro_precision + micro_recall)) if micro_precision and micro_recall and (micro_precision + micro_recall) > 0 else None

    n_gold_zero_label = int((df["gold_set"].apply(len) == 0).sum())
    n_classifier_zero_label = int((df["classifier_set"].apply(len) == 0).sum())

    # simplify confusion dict: top 3 confusions per direction per category
    confusion_summary = {}
    for cat in CATEGORIES:
        fp_conf = sorted(confusion[cat]["fp_confused_with"].items(), key=lambda x: -x[1])[:5]
        fn_conf = sorted(confusion[cat]["fn_confused_with"].items(), key=lambda x: -x[1])[:5]
        confusion_summary[cat] = {
            "fp_total": int(results.loc[results["category"] == cat, "FP"].iloc[0]),
            "fn_total": int(results.loc[results["category"] == cat, "FN"].iloc[0]),
            "when_classifier_wrongly_added_this_label_gold_actually_said": fp_conf,
            "when_classifier_wrongly_missed_this_label_classifier_actually_said": fn_conf,
        }

    summary = {
        "sample_size": n,
        "n_gold_zero_label_sentences": n_gold_zero_label,
        "n_classifier_zero_label_sentences": n_classifier_zero_label,
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_F1": round(macro_f1, 4),
        "micro_precision": round(micro_precision, 4) if micro_precision else None,
        "micro_recall": round(micro_recall, 4) if micro_recall else None,
        "micro_F1": round(micro_f1, 4) if micro_f1 else None,
        "per_category": results.to_dict(orient="records"),
        "confusion_summary": confusion_summary,
    }

    with open(BASE / "validation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(results.to_string(index=False))
    print(f"\nMacro precision: {macro_precision:.4f}")
    print(f"Macro recall:    {macro_recall:.4f}")
    print(f"Macro F1:        {macro_f1:.4f}")
    print(f"Micro precision: {micro_precision:.4f}")
    print(f"Micro recall:    {micro_recall:.4f}")
    print(f"Micro F1:        {micro_f1:.4f}")
    print(f"\nSample size: {n}")
    print(f"Gold zero-label sentences: {n_gold_zero_label}")
    print(f"Classifier zero-label sentences: {n_classifier_zero_label}")
    print(f"\nSaved -> {BASE / 'validation_results.csv'}")
    print(f"Saved -> {BASE / 'validation_summary.json'}")


if __name__ == "__main__":
    main()
