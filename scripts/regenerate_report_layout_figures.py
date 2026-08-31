"""Regenerate report figures whose source data already exists in saved results.

This layout-only script is intentionally independent of the removed raw ISOT CSVs.
It never recalculates a metric; it only redraws two figures from committed JSON/CSV
artifacts so labels and legends remain inside the exported image boundary.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/newslens-matplotlib")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "reports" / "figures"
RESULTS = ROOT / "reports" / "results"
PAPER = "#FAF8F2"
INK = "#1A1917"
MUTED = "#77736C"
LINE = "#D4CEC2"
PALETTE = ["#40352C", "#6D5947", "#A89984", "#8A693D"]


def editorial_axes(fig, ax) -> None:
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    ax.tick_params(colors=MUTED)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)
    ax.title.set_color(INK)
    for spine in ax.spines.values():
        spine.set_color(LINE)


def duplicate_record_analysis() -> None:
    profile = json.loads((RESULTS / "dataset_profile.json").read_text(encoding="utf-8"))
    labels = ["Eligible unique rows", "Exact duplicates removed", "Short / empty removed"]
    values = [profile["clean_rows"], profile["duplicates_removed"], profile["short_or_empty_rows_removed"]]

    fig, ax = plt.subplots(figsize=(8.8, 4.5), dpi=190)
    bars = ax.barh(labels, values, color=["#496454", "#6D5947", "#8A693D"])
    ax.bar_label(bars, labels=[f"{value:,}" for value in values], padding=5)
    ax.set_xlim(0, max(values) * 1.16)
    ax.set_title(f"Duplicate and eligibility audit (raw n={profile['raw_rows']:,})")
    ax.set_xlabel("Rows")
    ax.grid(axis="x", color=LINE, linewidth=0.8, alpha=0.8)
    ax.grid(axis="y", visible=False)
    editorial_axes(fig, ax)
    fig.tight_layout()
    fig.savefig(
        FIGURES / "duplicate_record_analysis.png",
        bbox_inches="tight",
        pad_inches=0.12,
        facecolor=PAPER,
    )
    plt.close(fig)


def model_comparison() -> None:
    with (RESULTS / "model_comparison.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    metric_names = ["accuracy", "macro_f1", "roc_auc", "pr_auc"]
    display_names = ["Accuracy", "Macro F1", "ROC AUC", "PR AUC"]
    colors = PALETTE
    x_positions = np.arange(len(rows))
    width = 0.19

    fig, ax = plt.subplots(figsize=(10.5, 5.3), dpi=190)
    for offset, (metric, display, color) in enumerate(zip(metric_names, display_names, colors)):
        ax.bar(
            x_positions + (offset - 1.5) * width,
            [float(row[metric]) for row in rows],
            width,
            label=display,
            color=color,
        )
    ax.set_xticks(x_positions, [row["model"] for row in rows], rotation=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Held-out model comparison", weight="bold")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.16), frameon=False)
    ax.grid(axis="y", color=LINE, linewidth=0.8, alpha=0.8)
    ax.grid(axis="x", visible=False)
    editorial_axes(fig, ax)
    fig.subplots_adjust(bottom=0.24, left=0.08, right=0.98, top=0.90)
    fig.savefig(
        FIGURES / "model_comparison.png",
        bbox_inches="tight",
        pad_inches=0.12,
        facecolor=PAPER,
    )
    plt.close(fig)


if __name__ == "__main__":
    FIGURES.mkdir(parents=True, exist_ok=True)
    duplicate_record_analysis()
    model_comparison()
    print("Regenerated duplicate_record_analysis.png and model_comparison.png")
