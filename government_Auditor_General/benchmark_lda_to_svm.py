from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC


ROOT = Path(__file__).resolve().parent
CORPUS_CSV = ROOT / "oag_infrastructure_sentence_corpus_2017_2025_expanded.csv"
SUMMARY_CSV = ROOT / "lda_to_svm_benchmark_summary.csv"
DETAILS_JSON = ROOT / "lda_to_svm_benchmark_details.json"
WRITEUP_MD = ROOT / "lda_to_svm_benchmark_writeup.md"

RANDOM_STATE = 42
N_TOPICS = 6


def evaluate_model(name: str, X_train, X_test, y_train, y_test) -> dict:
    clf = LinearSVC(class_weight="balanced", random_state=RANDOM_STATE, max_iter=4000)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)

    return {
        "model": name,
        "accuracy": float(accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_test, pred, average="weighted", zero_division=0)),
        "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0),
    }


def main() -> None:
    df = pd.read_csv(CORPUS_CSV)
    df["sentence"] = df["sentence"].fillna("")

    label_col = "driver_label_expanded" if "driver_label_expanded" in df.columns else "driver_label"
    y = df[label_col].fillna("unknown")

    # Common split indices for fair comparisons.
    indices = np.arange(len(df))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    # 1) Baseline TF-IDF -> SVM
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words="english")
    X_tfidf = tfidf.fit_transform(df["sentence"])
    X_tfidf_train = X_tfidf[train_idx]
    X_tfidf_test = X_tfidf[test_idx]

    baseline = evaluate_model("SVM_TFIDF", X_tfidf_train, X_tfidf_test, y_train, y_test)

    # 2) LDA topic proportions -> SVM
    count_vec = CountVectorizer(max_features=500, ngram_range=(1, 2), stop_words="english")
    X_count = count_vec.fit_transform(df["sentence"])

    lda = LatentDirichletAllocation(
        n_components=N_TOPICS,
        random_state=RANDOM_STATE,
        learning_method="batch",
        max_iter=40,
    )
    X_topic = lda.fit_transform(X_count)

    X_topic_train = X_topic[train_idx]
    X_topic_test = X_topic[test_idx]

    lda_only = evaluate_model("SVM_LDA_TOPICS", X_topic_train, X_topic_test, y_train, y_test)

    # 3) Hybrid TF-IDF + LDA topics -> SVM
    X_topic_sparse = csr_matrix(X_topic)
    X_hybrid = hstack([X_tfidf, X_topic_sparse], format="csr")
    X_hybrid_train = X_hybrid[train_idx]
    X_hybrid_test = X_hybrid[test_idx]

    hybrid = evaluate_model("SVM_TFIDF_PLUS_LDA", X_hybrid_train, X_hybrid_test, y_train, y_test)

    rows = []
    for r in [baseline, lda_only, hybrid]:
        rows.append(
            {
                "model": r["model"],
                "accuracy": r["accuracy"],
                "macro_f1": r["macro_f1"],
                "weighted_f1": r["weighted_f1"],
                "n_train": int(len(train_idx)),
                "n_test": int(len(test_idx)),
                "label_col": label_col,
                "n_topics": N_TOPICS,
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(SUMMARY_CSV, index=False)

    details = {
        "config": {
            "n_topics": N_TOPICS,
            "random_state": RANDOM_STATE,
            "label_col": label_col,
            "rows": int(len(df)),
            "n_train": int(len(train_idx)),
            "n_test": int(len(test_idx)),
        },
        "models": {
            baseline["model"]: {
                "accuracy": baseline["accuracy"],
                "macro_f1": baseline["macro_f1"],
                "weighted_f1": baseline["weighted_f1"],
                "classification_report": baseline["classification_report"],
            },
            lda_only["model"]: {
                "accuracy": lda_only["accuracy"],
                "macro_f1": lda_only["macro_f1"],
                "weighted_f1": lda_only["weighted_f1"],
                "classification_report": lda_only["classification_report"],
            },
            hybrid["model"]: {
                "accuracy": hybrid["accuracy"],
                "macro_f1": hybrid["macro_f1"],
                "weighted_f1": hybrid["weighted_f1"],
                "classification_report": hybrid["classification_report"],
            },
        },
    }
    DETAILS_JSON.write_text(json.dumps(details, indent=2), encoding="utf-8")

    best_row = summary.sort_values("macro_f1", ascending=False).iloc[0]

    writeup = (
        "# LDA to SVM Benchmark\n\n"
        f"Rows: {len(df)} | Label column: {label_col} | Topics: {N_TOPICS}\n\n"
        "## Summary\n\n"
        f"```\n{summary.round(6).to_string(index=False)}\n```\n\n"
        "## Interpretation\n"
        f"Best pipeline by macro-F1: **{best_row['model']}**\n\n"
        "## How LDA feeds SVM\n"
        "1. Fit LDA on document-term counts.\n"
        "2. Transform each sentence to topic-proportion vector.\n"
        "3. Use those vectors as SVM features (LDA-only), or concatenate with TF-IDF (hybrid).\n"
    )
    WRITEUP_MD.write_text(writeup, encoding="utf-8")

    print(f"Saved summary: {SUMMARY_CSV}")
    print(f"Saved details: {DETAILS_JSON}")
    print(f"Saved writeup: {WRITEUP_MD}")


if __name__ == "__main__":
    main()
