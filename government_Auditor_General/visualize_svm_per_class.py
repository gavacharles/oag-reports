from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


BASE_DIR = Path("/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General")
REPORT_FILE = BASE_DIR / "svm_driver_classification_report.json"
OUTPUT_DIR = BASE_DIR / "plots_png"
OUTPUT_FILE = OUTPUT_DIR / "svm_per_class_performance.png"
TOP_ONLY_OUTPUT_FILE = OUTPUT_DIR / "svm_per_class_performance_top_panel.png"
OUTPUT_FILE_SVG = OUTPUT_DIR / "svm_per_class_performance.svg"
TOP_ONLY_OUTPUT_FILE_SVG = OUTPUT_DIR / "svm_per_class_performance_top_panel.svg"


def load_svm_report() -> tuple[pd.DataFrame, dict]:
    report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
    excluded = {"accuracy", "macro avg", "weighted avg"}

    rows = []
    for label, metrics in report.items():
        if label in excluded:
            continue
        rows.append(
            {
                "class": label,
                "precision": metrics["precision"] * 100,
                "recall": metrics["recall"] * 100,
                "f1_score": metrics["f1-score"] * 100,
                "support": int(metrics["support"]),
            }
        )

    df = pd.DataFrame(rows).sort_values(["f1_score", "support"], ascending=[False, False])
    return df, report


def prettify(label: str) -> str:
    return label.replace("_", " ").title()


def plot_svm_per_class(df: pd.DataFrame, report: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="talk")

    pretty_labels = [prettify(label) for label in df["class"]]
    x = np.arange(len(df))
    width = 0.24

    def add_metric_labels(bar_groups, axis) -> None:
        for bars in bar_groups:
            for bar in bars:
                height = bar.get_height()
                axis.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 1.5,
                    f"{height:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    rotation=90,
                )

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(18, 12),
        gridspec_kw={"height_ratios": [3.2, 1.2], "hspace": 0.28},
    )

    bars_precision = ax1.bar(x - width, df["precision"], width, label="Precision", color="#1f77b4", alpha=0.9)
    bars_recall = ax1.bar(x, df["recall"], width, label="Recall", color="#ff7f0e", alpha=0.9)
    bars_f1 = ax1.bar(x + width, df["f1_score"], width, label="F1-Score", color="#2ca02c", alpha=0.9)

    ax1.set_title("SVM Per-Class Performance", fontsize=18, fontweight="bold", pad=14)
    ax1.set_ylabel("Score (%)", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(pretty_labels, rotation=22, ha="right", fontsize=11)
    ax1.set_ylim(0, 110)
    ax1.grid(axis="y", alpha=0.3, linestyle="--")
    ax1.legend(loc="upper right", ncol=3, frameon=True)

    add_metric_labels([bars_precision, bars_recall, bars_f1], ax1)

    support_colors = sns.color_palette("Blues", n_colors=len(df) + 2)[2:]
    support_bars = ax2.bar(pretty_labels, df["support"], color=support_colors, edgecolor="black", linewidth=0.8)
    ax2.set_title("Class Support in Test Set", fontsize=15, fontweight="bold", pad=10)
    ax2.set_ylabel("Support", fontweight="bold")
    ax2.set_xlabel("Dispute Driver Class", fontweight="bold")
    ax2.grid(axis="y", alpha=0.25, linestyle="--")
    ax2.tick_params(axis="x", rotation=22, labelsize=11)

    for bar, support in zip(support_bars, df["support"]):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"n={support}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    accuracy = report["accuracy"] * 100
    weighted_f1 = report["weighted avg"]["f1-score"] * 100
    macro_f1 = report["macro avg"]["f1-score"] * 100
    fig.suptitle(
        "Support Vector Machine (SVM) Classification Performance\nUganda OAG Infrastructure Dispute Drivers",
        fontsize=22,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        f"Overall accuracy: {accuracy:.2f}%   |   Weighted F1: {weighted_f1:.2f}%   |   Macro F1: {macro_f1:.2f}%",
        ha="center",
        fontsize=13,
    )

    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight", pad_inches=0.4)
    fig.savefig(OUTPUT_FILE_SVG, bbox_inches="tight", pad_inches=0.4)
    plt.close(fig)
    print(f"Saved SVM per-class visualization to: {OUTPUT_FILE}")
    print(f"Saved SVM per-class visualization to: {OUTPUT_FILE_SVG}")

    fig_top, ax_top = plt.subplots(figsize=(18, 8))
    top_precision = ax_top.bar(x - width, df["precision"], width, label="Precision", color="#1f77b4", alpha=0.9)
    top_recall = ax_top.bar(x, df["recall"], width, label="Recall", color="#ff7f0e", alpha=0.9)
    top_f1 = ax_top.bar(x + width, df["f1_score"], width, label="F1-Score", color="#2ca02c", alpha=0.9)

    ax_top.set_title("SVM Per-Class Performance", fontsize=18, fontweight="bold", pad=14)
    ax_top.set_ylabel("Score (%)", fontweight="bold")
    ax_top.set_xlabel("Dispute Driver Class", fontweight="bold")
    ax_top.set_xticks(x)
    ax_top.set_xticklabels(pretty_labels, rotation=22, ha="right", fontsize=11)
    ax_top.set_ylim(0, 110)
    ax_top.grid(axis="y", alpha=0.3, linestyle="--")
    ax_top.legend(loc="upper right", ncol=3, frameon=True)
    add_metric_labels([top_precision, top_recall, top_f1], ax_top)

    fig_top.suptitle(
        "Support Vector Machine (SVM) Classification Performance\nPer-Class Metrics Only",
        fontsize=22,
        fontweight="bold",
        y=0.98,
    )
    fig_top.text(
        0.5,
        0.01,
        f"Overall accuracy: {accuracy:.2f}%   |   Weighted F1: {weighted_f1:.2f}%   |   Macro F1: {macro_f1:.2f}%",
        ha="center",
        fontsize=13,
    )
    fig_top.tight_layout()
    fig_top.savefig(TOP_ONLY_OUTPUT_FILE, dpi=300, bbox_inches="tight", pad_inches=0.4)
    fig_top.savefig(TOP_ONLY_OUTPUT_FILE_SVG, bbox_inches="tight", pad_inches=0.4)
    plt.close(fig_top)
    print(f"Saved SVM top-panel visualization to: {TOP_ONLY_OUTPUT_FILE}")
    print(f"Saved SVM top-panel visualization to: {TOP_ONLY_OUTPUT_FILE_SVG}")


def main() -> None:
    df, report = load_svm_report()
    plot_svm_per_class(df, report)


if __name__ == "__main__":
    main()
