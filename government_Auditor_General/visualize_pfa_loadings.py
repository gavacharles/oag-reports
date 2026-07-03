from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import FactorAnalysis
from sklearn.feature_extraction.text import TfidfVectorizer


BASE_DIR = Path("/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General")
CORPUS_CSV = BASE_DIR / "oag_infrastructure_sentence_corpus_2017_2025.csv"
OUTPUT_DIR = BASE_DIR / "plots_png"
OUTPUT_FILE = OUTPUT_DIR / "pfa_factor_loadings.png"
OUTPUT_FILE_SVG = OUTPUT_DIR / "pfa_factor_loadings.svg"
LOADINGS_CSV = BASE_DIR / "pfa_factor_loadings_terms.csv"

FACTOR_TITLES = {
    1: "Factor 1 — Procurement Process Integrity",
    2: "Factor 2 — Financial Flow Management",
    3: "Factor 3 — Project Execution Quality",
    4: "Factor 4 — Regulatory Compliance",
    5: "Factor 5 — Resource Adequacy",
    6: "Factor 6 — Stakeholder Coordination",
}


def build_factor_model(sentences: pd.Series) -> tuple[pd.Index, pd.DataFrame]:
    vectorizer = TfidfVectorizer(max_features=400, ngram_range=(1, 2), stop_words="english")
    X = vectorizer.fit_transform(sentences)
    X_dense = X.toarray()

    n_components = 6 if X_dense.shape[0] > 20 else min(3, X_dense.shape[1])
    fa = FactorAnalysis(n_components=n_components, random_state=42, svd_method="lapack")
    fa.fit(X_dense)

    terms = pd.Index(vectorizer.get_feature_names_out(), name="term")
    loadings = pd.DataFrame(
        fa.components_.T,
        index=terms,
        columns=[f"factor_{i + 1}" for i in range(n_components)],
    )
    return terms, loadings


def top_terms(loadings: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    rows = []
    for factor in loadings.columns:
        subset = loadings[factor].abs().nlargest(top_n).index
        factor_df = loadings.loc[subset, [factor]].reset_index()
        factor_df.columns = ["term", "loading"]
        factor_df["factor"] = factor
        factor_df["direction"] = factor_df["loading"].apply(lambda value: "Positive" if value >= 0 else "Negative")
        rows.append(factor_df)
    result = pd.concat(rows, ignore_index=True)
    result["abs_loading"] = result["loading"].abs()
    return result


def plot_loadings(top_loadings: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    fig, axes = plt.subplots(2, 3, figsize=(24, 14))
    axes = axes.flatten()

    for i, factor in enumerate(sorted(top_loadings["factor"].unique(), key=lambda value: int(value.split("_")[1]))):
        ax = axes[i]
        factor_num = int(factor.split("_")[1])
        data = top_loadings[top_loadings["factor"] == factor].sort_values("loading")
        colors = data["direction"].map({"Positive": "#1f77b4", "Negative": "#d62728"})

        ax.barh(data["term"], data["loading"], color=colors, edgecolor="black", linewidth=0.7)
        ax.axvline(0, color="black", linestyle="--", linewidth=1)
        ax.set_title(FACTOR_TITLES.get(factor_num, factor.replace("_", " ").title()), fontweight="bold", fontsize=14, pad=10)
        ax.set_xlabel("Loading", fontweight="bold", fontsize=12)
        ax.set_ylabel("")
        ax.tick_params(axis="y", labelsize=10)
        ax.tick_params(axis="x", labelsize=10)

    handles = [
        plt.Line2D([0], [0], color="#1f77b4", lw=8, label="Positive loading"),
        plt.Line2D([0], [0], color="#d62728", lw=8, label="Negative loading"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=12)
    fig.suptitle(
        "Factor Analysis (FA): Term Loadings by Factor\nTop TF-IDF terms reconstructed from the original FA pipeline",
        fontsize=22,
        fontweight="bold",
        y=0.98,
    )
    fig.subplots_adjust(top=0.88, bottom=0.10, wspace=0.32, hspace=0.42)
    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight", pad_inches=0.4)
    fig.savefig(OUTPUT_FILE_SVG, bbox_inches="tight", pad_inches=0.4)
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus = pd.read_csv(CORPUS_CSV)
    _, loadings = build_factor_model(corpus["sentence"].fillna(""))
    top_loadings = top_terms(loadings, top_n=12)
    top_loadings.to_csv(LOADINGS_CSV, index=False)
    plot_loadings(top_loadings)
    print(f"Saved factor loadings figure to: {OUTPUT_FILE}")
    print(f"Saved factor loadings figure to: {OUTPUT_FILE_SVG}")
    print(f"Saved factor loadings table to: {LOADINGS_CSV}")


if __name__ == "__main__":
    main()
