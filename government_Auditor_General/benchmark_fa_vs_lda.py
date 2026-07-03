from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.decomposition import FactorAnalysis, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, normalized_mutual_info_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC


ROOT = Path(__file__).resolve().parent
CORPUS_CSV = ROOT / "oag_infrastructure_sentence_corpus_2017_2025_expanded.csv"
SUMMARY_CSV = ROOT / "fa_vs_lda_benchmark_summary.csv"
DETAIL_JSON = ROOT / "fa_vs_lda_benchmark_details.json"
TERMS_CSV = ROOT / "fa_vs_lda_top_terms.csv"
WRITEUP_MD = ROOT / "fa_vs_lda_benchmark_writeup.md"

N_COMPONENTS = 6
TOP_N_TERMS = 12
RANDOM_STATE = 42


def _safe_mean(values: List[float]) -> float:
    return float(np.mean(values)) if values else float("nan")


def _umass_coherence_from_indices(
    top_term_indices: List[int], binary_doc_term: np.ndarray
) -> float:
    """Compute UMass coherence for one topic/factor using a binary doc-term matrix.

    UMass for a topic with top terms w1..wN:
    mean_{i>j} log((D(w_i, w_j)+1)/D(w_j))
    """
    scores: List[float] = []

    for i in range(1, len(top_term_indices)):
        wi = top_term_indices[i]
        docs_wi = binary_doc_term[:, wi] > 0
        for j in range(i):
            wj = top_term_indices[j]
            docs_wj = binary_doc_term[:, wj] > 0

            d_wj = int(np.sum(docs_wj))
            d_wi_wj = int(np.sum(docs_wi & docs_wj))
            # +1 smoothing in numerator; denominator guarded against zero.
            score = np.log((d_wi_wj + 1) / max(d_wj, 1))
            scores.append(float(score))

    return _safe_mean(scores)


def _topic_diversity(term_lists: List[List[str]]) -> float:
    total = sum(len(t) for t in term_lists)
    unique = len(set(term for terms in term_lists for term in terms))
    return float(unique / total) if total else 0.0


def _extract_top_terms(components: np.ndarray, feature_names: np.ndarray, model_name: str) -> pd.DataFrame:
    rows = []
    for c_idx, weights in enumerate(components, start=1):
        top_idx = np.argsort(weights)[::-1][:TOP_N_TERMS]
        for rank, i in enumerate(top_idx, start=1):
            rows.append(
                {
                    "model": model_name,
                    "component": c_idx,
                    "rank": rank,
                    "term": feature_names[i],
                    "weight": float(weights[i]),
                }
            )
    return pd.DataFrame(rows)


def _classification_with_latent(latent_features: np.ndarray, labels: pd.Series) -> Dict[str, float]:
    # Keep classes with at least 2 samples so stratified split is valid.
    counts = labels.value_counts()
    keep = labels.isin(counts[counts >= 2].index)

    X = latent_features[keep.values]
    y = labels[keep].copy()

    if len(y.unique()) < 2 or len(y) < 30:
        return {"accuracy": float("nan"), "macro_f1": float("nan"), "n_train": 0, "n_test": 0}

    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(
        idx,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    clf = LinearSVC(class_weight="balanced", random_state=RANDOM_STATE, max_iter=3000)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)

    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro", zero_division=0)),
        "n_train": int(len(train_idx)),
        "n_test": int(len(test_idx)),
    }


def main() -> None:
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    df = pd.read_csv(CORPUS_CSV)
    df["sentence"] = df["sentence"].fillna("")

    # Prefer expanded labels for 13-category benchmark.
    label_col = "driver_label_expanded" if "driver_label_expanded" in df.columns else "driver_label"
    labels = df[label_col].fillna("unknown")

    # ---------------------------
    # Factor Analysis branch
    # ---------------------------
    fa_vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words="english")
    X_tfidf = fa_vectorizer.fit_transform(df["sentence"])
    X_tfidf_dense = X_tfidf.toarray()

    fa = FactorAnalysis(
        n_components=N_COMPONENTS,
        random_state=RANDOM_STATE,
        svd_method="lapack",
    )
    fa_scores = fa.fit_transform(X_tfidf_dense)

    fa_components = fa.components_  # shape: (n_components, n_features)
    fa_feature_names = fa_vectorizer.get_feature_names_out()

    # Reconstruction MSE proxy.
    recon = fa_scores @ fa_components + fa.mean_
    fa_recon_mse = float(np.mean((X_tfidf_dense - recon) ** 2))

    # For coherence on FA terms, build a binary count matrix with FA vocabulary.
    fa_count_vectorizer = CountVectorizer(vocabulary=fa_vectorizer.vocabulary_)
    fa_counts = fa_count_vectorizer.fit_transform(df["sentence"]).toarray()
    fa_binary = (fa_counts > 0).astype(int)

    fa_term_lists: List[List[str]] = []
    fa_coherences: List[float] = []
    for comp in fa_components:
        top_idx = np.argsort(comp)[::-1][:TOP_N_TERMS].tolist()
        fa_term_lists.append([fa_feature_names[i] for i in top_idx])
        fa_coherences.append(_umass_coherence_from_indices(top_idx, fa_binary))

    fa_topic_div = _topic_diversity(fa_term_lists)
    fa_coherence = _safe_mean(fa_coherences)

    # Dominant factor by magnitude.
    fa_dominant = np.argmax(np.abs(fa_scores), axis=1)
    fa_nmi = float(normalized_mutual_info_score(labels, fa_dominant))

    fa_cls = _classification_with_latent(fa_scores, labels)
    fa_terms_df = _extract_top_terms(fa_components, fa_feature_names, "FA")

    # ---------------------------
    # LDA branch
    # ---------------------------
    lda_vectorizer = CountVectorizer(max_features=500, ngram_range=(1, 2), stop_words="english")
    X_count = lda_vectorizer.fit_transform(df["sentence"])

    lda = LatentDirichletAllocation(
        n_components=N_COMPONENTS,
        random_state=RANDOM_STATE,
        learning_method="batch",
        max_iter=40,
        evaluate_every=-1,
    )
    lda_doc_topic = lda.fit_transform(X_count)

    lda_components = lda.components_
    lda_feature_names = lda_vectorizer.get_feature_names_out()

    lda_binary = (X_count.toarray() > 0).astype(int)

    lda_term_lists: List[List[str]] = []
    lda_coherences: List[float] = []
    for comp in lda_components:
        top_idx = np.argsort(comp)[::-1][:TOP_N_TERMS].tolist()
        lda_term_lists.append([lda_feature_names[i] for i in top_idx])
        lda_coherences.append(_umass_coherence_from_indices(top_idx, lda_binary))

    lda_topic_div = _topic_diversity(lda_term_lists)
    lda_coherence = _safe_mean(lda_coherences)

    lda_dominant = np.argmax(lda_doc_topic, axis=1)
    lda_nmi = float(normalized_mutual_info_score(labels, lda_dominant))

    lda_cls = _classification_with_latent(lda_doc_topic, labels)
    lda_terms_df = _extract_top_terms(lda_components, lda_feature_names, "LDA")

    lda_perplexity = float(lda.perplexity(X_count))
    lda_log_likelihood = float(lda.score(X_count))

    # ---------------------------
    # Save outputs
    # ---------------------------
    summary = pd.DataFrame(
        [
            {
                "model": "FA",
                "n_components": N_COMPONENTS,
                "topic_diversity": fa_topic_div,
                "umass_coherence": fa_coherence,
                "label_alignment_nmi": fa_nmi,
                "latent_cls_accuracy": fa_cls["accuracy"],
                "latent_cls_macro_f1": fa_cls["macro_f1"],
                "reconstruction_mse": fa_recon_mse,
                "perplexity": np.nan,
                "log_likelihood": np.nan,
            },
            {
                "model": "LDA",
                "n_components": N_COMPONENTS,
                "topic_diversity": lda_topic_div,
                "umass_coherence": lda_coherence,
                "label_alignment_nmi": lda_nmi,
                "latent_cls_accuracy": lda_cls["accuracy"],
                "latent_cls_macro_f1": lda_cls["macro_f1"],
                "reconstruction_mse": np.nan,
                "perplexity": lda_perplexity,
                "log_likelihood": lda_log_likelihood,
            },
        ]
    )
    summary.to_csv(SUMMARY_CSV, index=False)

    terms = pd.concat([fa_terms_df, lda_terms_df], ignore_index=True)
    terms.to_csv(TERMS_CSV, index=False)

    details = {
        "config": {
            "n_components": N_COMPONENTS,
            "top_n_terms": TOP_N_TERMS,
            "random_state": RANDOM_STATE,
            "label_column": label_col,
            "rows": int(len(df)),
        },
        "fa": {
            "topic_diversity": fa_topic_div,
            "umass_coherence": fa_coherence,
            "label_alignment_nmi": fa_nmi,
            "latent_cls": fa_cls,
            "reconstruction_mse": fa_recon_mse,
            "top_terms": fa_term_lists,
        },
        "lda": {
            "topic_diversity": lda_topic_div,
            "umass_coherence": lda_coherence,
            "label_alignment_nmi": lda_nmi,
            "latent_cls": lda_cls,
            "perplexity": lda_perplexity,
            "log_likelihood": lda_log_likelihood,
            "top_terms": lda_term_lists,
        },
    }
    DETAIL_JSON.write_text(json.dumps(details, indent=2), encoding="utf-8")

    better_coherence = "LDA" if lda_coherence > fa_coherence else "FA"
    better_macro_f1 = "LDA" if lda_cls["macro_f1"] > fa_cls["macro_f1"] else "FA"

    summary_text = summary.round(6).to_string(index=False)
    writeup = f"""# FA vs LDA Benchmark (Side-by-Side)\n\n## Corpus\n- Rows: {len(df)}\n- Label column: {label_col}\n- Components/topics: {N_COMPONENTS}\n\n## Metric Summary\n\n```\n{summary_text}\n```\n\n## Quick Interpretation\n- Better topic coherence (UMass): **{better_coherence}**\n- Better latent-feature classification (macro F1): **{better_macro_f1}**\n\n## Notes\n- FA branch uses TF-IDF + `sklearn.decomposition.FactorAnalysis`.\n- LDA branch uses CountVectorizer + `sklearn.decomposition.LatentDirichletAllocation`.\n- UMass coherence is computed from top {TOP_N_TERMS} terms per component/topic.\n"""
    WRITEUP_MD.write_text(writeup, encoding="utf-8")

    print(f"Saved summary: {SUMMARY_CSV}")
    print(f"Saved details: {DETAIL_JSON}")
    print(f"Saved top terms: {TERMS_CSV}")
    print(f"Saved writeup: {WRITEUP_MD}")


if __name__ == "__main__":
    main()
