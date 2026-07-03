from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path("/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General")
CORPUS_CSV = BASE_DIR / "oag_infrastructure_sentence_corpus_2017_2025.csv"
OUTPUT_DIR = BASE_DIR / "plots_png"
OUTPUT_FILE = OUTPUT_DIR / "initial_taxonomy_pre_reclassification.png"
OUTPUT_FILE_SVG = OUTPUT_DIR / "initial_taxonomy_pre_reclassification.svg"

LABEL_MAP = {
    "other": "Other",
    "procurement_irregularities": "Procurement Irregularities",
    "delayed_payments": "Delayed Payments",
    "contract_management": "Contract Management",
    "governance_and_controls": "Governance and Controls",
    "land_and_right_of_way": "Land and Right of Way",
    "claims_and_liabilities": "Claims and Liabilities",
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    corpus_df = pd.read_csv(CORPUS_CSV)
    df = (
        corpus_df["driver_label"]
        .value_counts(dropna=False)
        .rename_axis("driver")
        .reset_index(name="count")
    )

    df["label"] = df["driver"].map(LABEL_MAP).fillna(df["driver"].str.replace("_", " ").str.title())
    df = df.sort_values("count", ascending=True).reset_index(drop=True)

    total = int(df["count"].sum())
    df["share_pct"] = (df["count"] / total) * 100

    sns.set_theme(style="whitegrid", context="talk")
    fig, ax = plt.subplots(figsize=(14, 8))

    colors = sns.color_palette("Blues", n_colors=len(df) + 2)[2:]
    bars = ax.barh(df["label"], df["count"], color=colors, edgecolor="black", linewidth=1)

    for bar, count, pct in zip(bars, df["count"], df["share_pct"]):
        ax.text(
            bar.get_width() + max(df["count"]) * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{count} ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_title("Initial Taxonomy Before Reclassification (2017–2025)", fontweight="bold", fontsize=18, pad=12)
    ax.set_xlabel("Sentence Mentions", fontweight="bold", fontsize=13)
    ax.set_ylabel("Initial Driver Categories", fontweight="bold", fontsize=13)
    ax.set_xlim(0, df["count"].max() * 1.25)
    ax.grid(axis="x", alpha=0.35)

    fig.suptitle(
        f"Uganda OAG Infrastructure Corpus — Pre-Reclassification Taxonomy (n={total} mentions)",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight", pad_inches=0.3)
    fig.savefig(OUTPUT_FILE_SVG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    print(f"Saved initial taxonomy visualization to: {OUTPUT_FILE}")
    print(f"Saved initial taxonomy visualization to: {OUTPUT_FILE_SVG}")


if __name__ == "__main__":
    main()
