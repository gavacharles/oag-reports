"""
Visualization script for FA vs LDA benchmark and LDA-to-SVM pipeline comparison.
Generates side-by-side comparison plots for model performance metrics.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path("/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General")
FA_LDA_SUMMARY = BASE_DIR / "fa_vs_lda_benchmark_summary.csv"
SVM_SUMMARY = BASE_DIR / "lda_to_svm_benchmark_summary.csv"
OUTPUT_DIR = BASE_DIR / "plots_png"

OUTPUT_FILE_FA_LDA_TOP = OUTPUT_DIR / "fa_vs_lda_benchmark_comparison_top_panel.png"
OUTPUT_FILE_FA_LDA_TOP_SVG = OUTPUT_DIR / "fa_vs_lda_benchmark_comparison_top_panel.svg"
OUTPUT_FILE_FA_LDA_BOTTOM = OUTPUT_DIR / "fa_vs_lda_benchmark_comparison_bottom_panel.png"
OUTPUT_FILE_FA_LDA_BOTTOM_SVG = OUTPUT_DIR / "fa_vs_lda_benchmark_comparison_bottom_panel.svg"
OUTPUT_FILE_SVM = OUTPUT_DIR / "lda_to_svm_pipeline_comparison.png"
OUTPUT_FILE_SVM_SVG = OUTPUT_DIR / "lda_to_svm_pipeline_comparison.svg"


def plot_fa_vs_lda_benchmark() -> None:
    """Create split top-panel and bottom-panel plots for FA vs LDA benchmark metrics."""
    df = pd.read_csv(FA_LDA_SUMMARY)
    df = df[["model", "topic_diversity", "umass_coherence", "label_alignment_nmi", "latent_cls_macro_f1"]]

    sns.set_theme(style="whitegrid", context="talk")
    metrics = [
        ("topic_diversity", "Topic Diversity (0–1)", "higher is better", "#2ecc71"),
        ("umass_coherence", "UMass Coherence (log scale)", "higher is better", "#3498db"),
        ("label_alignment_nmi", "Label Alignment NMI (0–1)", "higher is better", "#e74c3c"),
        ("latent_cls_macro_f1", "Latent Classification Macro-F1", "higher is better", "#f39c12"),
    ]

    def _plot_panel(panel_metrics: list[tuple[str, str, str, str]], panel_title: str, output_png: Path, output_svg: Path) -> None:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6.5))
        for idx, (col, title, direction, color) in enumerate(panel_metrics):
            ax = axes[idx]
            values = df[col].values
            models = df["model"].values

            bars = ax.bar(models, values, color=[color, color], alpha=0.8, edgecolor="black", linewidth=2)

            for bar, val in zip(bars, values):
                label_y = val + (0.02 * (max(values) - min(values) + 1e-6)) if val >= 0 else val - (0.04 * (max(values) - min(values) + 1e-6))
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    label_y,
                    f"{val:.3f}",
                    ha="center",
                    va="bottom" if val >= 0 else "top",
                    fontweight="bold",
                    fontsize=12,
                )

            y_min = min(values)
            y_max = max(values)
            spread = y_max - y_min
            margin = 0.12 * spread if spread > 0 else 0.1 * (abs(y_max) + 1)
            ax.set_ylim(y_min - margin, y_max + margin)
            ax.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.5)
            ax.set_ylabel("Score", fontweight="bold", fontsize=12)
            ax.set_title(f"{title}\n({direction})", fontweight="bold", fontsize=13, pad=10)
            ax.tick_params(axis="x", labelsize=11)
            ax.tick_params(axis="y", labelsize=11)
            ax.grid(axis="y", alpha=0.3)

        fig.suptitle(panel_title, fontsize=18, fontweight="bold", y=0.98)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(output_png, dpi=300, bbox_inches="tight", pad_inches=0.3)
        fig.savefig(output_svg, bbox_inches="tight", pad_inches=0.3)
        plt.close(fig)

    _plot_panel(
        panel_metrics=metrics[:2],
        panel_title="Factor Analysis (FA) vs Latent Dirichlet Allocation (LDA)\nBenchmark Comparison — Top Panel",
        output_png=OUTPUT_FILE_FA_LDA_TOP,
        output_svg=OUTPUT_FILE_FA_LDA_TOP_SVG,
    )
    _plot_panel(
        panel_metrics=metrics[2:],
        panel_title="Factor Analysis (FA) vs Latent Dirichlet Allocation (LDA)\nBenchmark Comparison — Bottom Panel",
        output_png=OUTPUT_FILE_FA_LDA_BOTTOM,
        output_svg=OUTPUT_FILE_FA_LDA_BOTTOM_SVG,
    )

    print(f"Saved FA vs LDA top-panel visualization to: {OUTPUT_FILE_FA_LDA_TOP}")
    print(f"Saved FA vs LDA top-panel visualization to: {OUTPUT_FILE_FA_LDA_TOP_SVG}")
    print(f"Saved FA vs LDA bottom-panel visualization to: {OUTPUT_FILE_FA_LDA_BOTTOM}")
    print(f"Saved FA vs LDA bottom-panel visualization to: {OUTPUT_FILE_FA_LDA_BOTTOM_SVG}")


def plot_svm_pipeline_comparison() -> None:
    """Create comparison plots for the three SVM pipeline strategies."""
    df = pd.read_csv(SVM_SUMMARY)
    df["pipeline"] = df["model"].str.replace("SVM_", "").str.replace("_", "\n")

    sns.set_theme(style="whitegrid", context="talk")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    metrics = [
        ("accuracy", "Accuracy", "#1abc9c"),
        ("macro_f1", "Macro-averaged F1 Score", "#9b59b6"),
        ("weighted_f1", "Weighted F1 Score", "#e67e22"),
    ]

    for idx, (col, title, color) in enumerate(metrics):
        ax = axes[idx]
        values = df[col].values
        pipelines = df["pipeline"].values

        bars = ax.bar(range(len(pipelines)), values, color=color, alpha=0.8, edgecolor="black", linewidth=2)

        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{val:.3f}",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=11,
            )

        ax.set_ylabel("Score", fontweight="bold", fontsize=12)
        ax.set_title(title, fontweight="bold", fontsize=13, pad=10)
        ax.set_xticks(range(len(pipelines)))
        ax.set_xticklabels(pipelines, fontsize=10, fontweight="bold")
        ax.set_ylim(0, 1.0)
        ax.tick_params(axis="y", labelsize=11)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle(
        "LDA-to-SVM Pipeline Comparison\nThree Feature Engineering Strategies on Classification Task",
        fontsize=18,
        fontweight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUTPUT_FILE_SVM, dpi=300, bbox_inches="tight", pad_inches=0.3)
    fig.savefig(OUTPUT_FILE_SVM_SVG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    print(f"Saved SVM pipeline comparison visualization to: {OUTPUT_FILE_SVM}")
    print(f"Saved SVM pipeline comparison visualization to: {OUTPUT_FILE_SVM_SVG}")


def plot_combined_comparison() -> None:
    """Create a combined figure showing both benchmarks side-by-side."""
    fa_lda_df = pd.read_csv(FA_LDA_SUMMARY)
    svm_df = pd.read_csv(SVM_SUMMARY)

    sns.set_theme(style="whitegrid", context="talk")
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)

    # FA vs LDA metrics (top row, left 2 columns)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    fa_lda_metrics = [
        (ax1, "topic_diversity", "Topic Diversity", "#2ecc71"),
        (ax2, "umass_coherence", "UMass Coherence", "#3498db"),
    ]

    for ax, col, title, color in fa_lda_metrics:
        values = fa_lda_df[col].values
        models = fa_lda_df["model"].values
        bars = ax.bar(models, values, color=color, alpha=0.8, edgecolor="black", linewidth=2)
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{val:.3f}",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=11,
            )
        ax.set_ylabel("Score", fontweight="bold")
        ax.set_title(title, fontweight="bold", fontsize=12)
        ax.grid(axis="y", alpha=0.3)

    # SVM comparison (top row, right 1 column)
    ax3 = fig.add_subplot(gs[0, 2])
    svm_df_plot = svm_df.copy()
    svm_df_plot["pipeline"] = svm_df_plot["model"].str.replace("SVM_", "").str.replace("_", "\n")
    bars = ax3.bar(range(len(svm_df_plot)), svm_df_plot["macro_f1"].values, color="#9b59b6", alpha=0.8, edgecolor="black", linewidth=2)
    for i, (bar, val) in enumerate(zip(bars, svm_df_plot["macro_f1"].values)):
        height = bar.get_height()
        ax3.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )
    ax3.set_ylabel("Macro-F1 Score", fontweight="bold")
    ax3.set_title("SVM Macro-F1 Performance", fontweight="bold", fontsize=12)
    ax3.set_xticks(range(len(svm_df_plot)))
    ax3.set_xticklabels(svm_df_plot["pipeline"].values, fontsize=9, fontweight="bold")
    ax3.set_ylim(0, 1.0)
    ax3.grid(axis="y", alpha=0.3)

    # Bottom row: Summary metrics
    ax4 = fig.add_subplot(gs[1, :])
    ax4.axis("off")

    summary_text = f"""
FA vs LDA Summary:
  • LDA Topic Diversity: {fa_lda_df.loc[fa_lda_df['model']=='LDA', 'topic_diversity'].values[0]:.3f} vs FA: {fa_lda_df.loc[fa_lda_df['model']=='FA', 'topic_diversity'].values[0]:.3f}
  • LDA UMass Coherence: {fa_lda_df.loc[fa_lda_df['model']=='LDA', 'umass_coherence'].values[0]:.3f} vs FA: {fa_lda_df.loc[fa_lda_df['model']=='FA', 'umass_coherence'].values[0]:.3f}
  • LDA Label Alignment NMI: {fa_lda_df.loc[fa_lda_df['model']=='LDA', 'label_alignment_nmi'].values[0]:.3f} vs FA: {fa_lda_df.loc[fa_lda_df['model']=='FA', 'label_alignment_nmi'].values[0]:.3f}
  ⟹ Conclusion: LDA produces better topic quality metrics than FA

SVM Pipeline Summary:
  • TF-IDF Only: Accuracy={svm_df.loc[svm_df['model']=='SVM_TFIDF', 'accuracy'].values[0]:.3f}, Macro-F1={svm_df.loc[svm_df['model']=='SVM_TFIDF', 'macro_f1'].values[0]:.3f}
  • LDA Topics Only: Accuracy={svm_df.loc[svm_df['model']=='SVM_LDA_TOPICS', 'accuracy'].values[0]:.3f}, Macro-F1={svm_df.loc[svm_df['model']=='SVM_LDA_TOPICS', 'macro_f1'].values[0]:.3f}
  • TF-IDF + LDA (Hybrid): Accuracy={svm_df.loc[svm_df['model']=='SVM_TFIDF_PLUS_LDA', 'accuracy'].values[0]:.3f}, Macro-F1={svm_df.loc[svm_df['model']=='SVM_TFIDF_PLUS_LDA', 'macro_f1'].values[0]:.3f}
  ⟹ Conclusion: TF-IDF alone remains superior for supervised classification; LDA topics do not improve performance
"""

    ax4.text(
        0.05,
        0.5,
        summary_text,
        transform=ax4.transAxes,
        fontsize=11,
        verticalalignment="center",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.3),
    )

    fig.suptitle(
        "Benchmark Analysis: Factor Analysis vs LDA & SVM Pipeline Strategies",
        fontsize=19,
        fontweight="bold",
        y=0.98,
    )

    fig.savefig(OUTPUT_DIR / "benchmark_combined_comparison.png", dpi=300, bbox_inches="tight", pad_inches=0.4)
    fig.savefig(OUTPUT_DIR / "benchmark_combined_comparison.svg", bbox_inches="tight", pad_inches=0.4)
    plt.close(fig)

    print(f"Saved combined benchmark visualization to: {OUTPUT_DIR / 'benchmark_combined_comparison.png'}")
    print(f"Saved combined benchmark visualization to: {OUTPUT_DIR / 'benchmark_combined_comparison.svg'}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plot_fa_vs_lda_benchmark()
    plot_svm_pipeline_comparison()
    plot_combined_comparison()


if __name__ == "__main__":
    main()
