from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path("/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General")
INPUT_CSV = BASE_DIR / "pfa_factor_scores_2017_2025.csv"
OUTPUT_DIR = BASE_DIR / "plots_png"
TOP_OUTPUT_FILE = OUTPUT_DIR / "pfa_factor_trends.png"
BOTTOM_OUTPUT_FILE = OUTPUT_DIR / "pfa_factor_distribution_correlation.png"
TOP_OUTPUT_FILE_SVG = OUTPUT_DIR / "pfa_factor_trends.svg"
BOTTOM_OUTPUT_FILE_SVG = OUTPUT_DIR / "pfa_factor_distribution_correlation.svg"

FACTOR_LABELS = {
    "factor_1": "Factor 1\nProcurement Process Integrity",
    "factor_2": "Factor 2\nFinancial Flow Management",
    "factor_3": "Factor 3\nProject Execution Quality",
    "factor_4": "Factor 4\nRegulatory Compliance",
    "factor_5": "Factor 5\nResource Adequacy",
    "factor_6": "Factor 6\nStakeholder Coordination",
}

HEATMAP_SHORT_LABELS = {
    "Factor 1\nProcurement Process Integrity": "F1",
    "Factor 2\nFinancial Flow Management": "F2",
    "Factor 3\nProject Execution Quality": "F3",
    "Factor 4\nRegulatory Compliance": "F4",
    "Factor 5\nResource Adequacy": "F5",
    "Factor 6\nStakeholder Coordination": "F6",
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_CSV)
    factor_columns = [column for column in df.columns if column.startswith("factor_")]

    renamed = df.rename(columns=FACTOR_LABELS)
    labeled_factor_columns = [FACTOR_LABELS[column] for column in factor_columns]

    yearly_means = renamed.groupby("year")[labeled_factor_columns].mean()
    long_df = renamed.melt(
        id_vars="year",
        value_vars=labeled_factor_columns,
        var_name="factor",
        value_name="score",
    )
    correlations = renamed[labeled_factor_columns].corr()

    sns.set_theme(style="whitegrid", context="talk")
    fig_top, ax1 = plt.subplots(figsize=(18, 9))
    palette = sns.color_palette("tab10", n_colors=len(labeled_factor_columns))
    for color, factor in zip(palette, labeled_factor_columns):
        ax1.plot(
            yearly_means.index,
            yearly_means[factor],
            marker="o",
            linewidth=2.5,
            markersize=7,
            label=factor.replace("\n", " — "),
            color=color,
        )

    ax1.axhline(0, color="black", linewidth=1, linestyle="--", alpha=0.6)
    ax1.set_title("Factor Analysis (FA) — Factor Trajectories by Year", fontweight="bold", pad=12)
    ax1.set_xlabel("Year", fontweight="bold")
    ax1.set_ylabel("Mean factor score", fontweight="bold")
    ax1.set_xticks(yearly_means.index)
    ax1.legend(loc="upper left", bbox_to_anchor=(1.01, 1.02), frameon=True, title="Latent factors")
    fig_top.suptitle(
        "Factor Analysis (FA) Overview\nUganda OAG Infrastructure Corpus (2018–2025)",
        fontsize=22,
        fontweight="bold",
        y=0.98,
    )
    fig_top.tight_layout()
    fig_top.savefig(TOP_OUTPUT_FILE, dpi=300, bbox_inches="tight", pad_inches=0.4)
    fig_top.savefig(TOP_OUTPUT_FILE_SVG, bbox_inches="tight", pad_inches=0.4)
    plt.close(fig_top)

    fig_bottom, (ax2, ax3) = plt.subplots(figsize=(22, 10), ncols=2)
    sns.boxplot(
        data=long_df,
        x="score",
        y="factor",
        hue="factor",
        dodge=False,
        palette="Set2",
        linewidth=1,
        fliersize=2,
        ax=ax2,
    )
    if ax2.legend_ is not None:
        ax2.legend_.remove()
    ax2.axvline(0, color="black", linewidth=1, linestyle="--", alpha=0.6)
    ax2.set_title("Distribution of factor scores", fontweight="bold", pad=10)
    ax2.set_xlabel("Factor score", fontweight="bold")
    ax2.set_ylabel("")
    ax2.tick_params(axis="y", labelsize=11)
    ax2.tick_params(axis="x", labelsize=11)

    sns.heatmap(
        correlations,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"label": "Correlation", "shrink": 0.82},
        ax=ax3,
    )
    ax3.set_title("Correlation between FA Factors", fontweight="bold", pad=10)
    ax3.set_xlabel("")
    ax3.set_ylabel("")
    ax3.set_xticklabels(
        [HEATMAP_SHORT_LABELS[label] for label in correlations.columns],
        rotation=0,
        ha="center",
        fontsize=12,
        fontweight="bold",
    )
    ax3.set_yticklabels(correlations.index, rotation=0, fontsize=11)
    ax3.tick_params(axis="x", pad=8)
    ax3.tick_params(axis="y", labelrotation=0, labelsize=11)

    fig_bottom.suptitle(
        "Factor Analysis (FA) Overview\nDistribution and Correlation of Latent Factors",
        fontsize=22,
        fontweight="bold",
        y=0.98,
    )
    fig_bottom.subplots_adjust(top=0.84, wspace=0.48)
    fig_bottom.savefig(BOTTOM_OUTPUT_FILE, dpi=300, bbox_inches="tight", pad_inches=0.4)
    fig_bottom.savefig(BOTTOM_OUTPUT_FILE_SVG, bbox_inches="tight", pad_inches=0.4)
    plt.close(fig_bottom)
    print(f"Saved PFA visualization to: {TOP_OUTPUT_FILE}")
    print(f"Saved PFA visualization to: {TOP_OUTPUT_FILE_SVG}")
    print(f"Saved PFA visualization to: {BOTTOM_OUTPUT_FILE}")
    print(f"Saved PFA visualization to: {BOTTOM_OUTPUT_FILE_SVG}")


if __name__ == "__main__":
    main()
