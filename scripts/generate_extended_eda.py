"""Generate additional report-grade EDA figures from the official ISOT CSVs."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/newslens-matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import FIGURES_DIR, RANDOM_SEED, RAW_DATA_DIR  # noqa: E402
from training.prepare_dataset import load_isot_dataset  # noqa: E402


COLORS = {0: "#496454", 1: "#813F39"}
LABELS = {0: "Reliable", 1: "Misleading"}


def finish(fig, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / filename, bbox_inches="tight", dpi=190)
    plt.close(fig)
    print(filename)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=0.95)
    frame, profile = load_isot_dataset(RAW_DATA_DIR, max_rows=24_000)
    frame["Class"] = frame["label"].map(LABELS)
    frame["title_word_count"] = frame["title"].str.split().str.len()
    frame["sentence_count"] = frame["text"].map(
        lambda value: max(1, len([part for part in re.split(r"(?<=[.!?])\s+", str(value)) if part.strip()]))
    )
    frame["avg_sentence_length"] = frame["word_count"] / frame["sentence_count"]
    plot = frame.sample(n=min(12_000, len(frame)), random_state=RANDOM_SEED)

    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    sns.histplot(data=plot, x="title_word_count", hue="Class", bins=35, stat="density", common_norm=False, element="step", palette={"Reliable": COLORS[0], "Misleading": COLORS[1]}, ax=ax)
    ax.set_xlim(0, float(plot["title_word_count"].quantile(0.99)))
    ax.set(title=f"Title-length distribution by class (sample n={len(plot):,})", xlabel="Title word count (99th percentile view)", ylabel="Density")
    finish(fig, "title_length_distribution.png")

    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    sns.boxplot(data=plot, x="Class", y="avg_sentence_length", hue="Class", palette={"Reliable": COLORS[0], "Misleading": COLORS[1]}, legend=False, showfliers=False, ax=ax)
    ax.set_ylim(0, float(plot["avg_sentence_length"].quantile(0.98)))
    ax.set(title=f"Average sentence length by class (sample n={len(plot):,})", xlabel="ISOT label", ylabel="Words per sentence")
    finish(fig, "average_sentence_length.png")

    true_raw = pd.read_csv(RAW_DATA_DIR / "True.csv").assign(Class="Reliable")
    fake_raw = pd.read_csv(RAW_DATA_DIR / "Fake.csv").assign(Class="Misleading")
    raw = pd.concat([true_raw, fake_raw], ignore_index=True)
    missing = raw.groupby("Class")[["title", "text", "subject", "date"]].apply(lambda data: data.isna().mean() * 100)
    fig, ax = plt.subplots(figsize=(8.6, 3.7))
    sns.heatmap(missing, annot=True, fmt=".2f", cmap=sns.light_palette("#813F39", as_cmap=True), vmin=0, ax=ax, cbar_kws={"label": "Missing (%)"})
    ax.set(title=f"Missing-value audit in raw ISOT files (n={len(raw):,})", xlabel="Column", ylabel="Source label")
    finish(fig, "missing_values_heatmap.png")

    removed = pd.DataFrame(
        {
            "Quality outcome": ["Eligible unique rows", "Exact duplicates removed", "Short / empty removed"],
            "Rows": [profile["clean_rows"], profile["duplicates_removed"], profile["short_or_empty_rows_removed"]],
        }
    )
    fig, ax = plt.subplots(figsize=(8.8, 4.5))
    bars = ax.barh(removed["Quality outcome"], removed["Rows"], color=["#496454", "#6D5947", "#8A693D"])
    ax.bar_label(bars, labels=[f"{value:,}" for value in removed["Rows"]], padding=5)
    ax.set_xlim(0, float(removed["Rows"].max()) * 1.16)
    ax.set(title=f"Duplicate and eligibility audit (raw n={profile['raw_rows']:,})", xlabel="Rows")
    finish(fig, "duplicate_record_analysis.png")

    vocab_rows = []
    ngram_rows = []
    for label in (0, 1):
        texts = frame.loc[frame["label"] == label, "combined"].sample(n=4_000, random_state=RANDOM_SEED)
        unigram = CountVectorizer(stop_words="english", min_df=2)
        unigram.fit(texts)
        vocab_rows.append({"Class": LABELS[label], "Unique unigrams": len(unigram.get_feature_names_out())})
        for n in (1, 2, 3):
            vectorizer = CountVectorizer(stop_words="english", ngram_range=(n, n), max_features=8_000)
            matrix = vectorizer.fit_transform(texts)
            totals = np.asarray(matrix.sum(axis=0)).ravel()
            names = np.asarray(vectorizer.get_feature_names_out())
            for index in np.argsort(totals)[-5:]:
                ngram_rows.append({"Class": LABELS[label], "n": n, "term": names[index], "count": int(totals[index])})
    vocab = pd.DataFrame(vocab_rows)
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    bars = ax.bar(vocab["Class"], vocab["Unique unigrams"], color=[COLORS[0], COLORS[1]])
    ax.bar_label(bars, labels=[f"{value:,}" for value in vocab["Unique unigrams"]], padding=5)
    ax.set(title="Vocabulary-size comparison (4,000 articles per class; min_df=2)", ylabel="Unique non-stopword unigrams")
    finish(fig, "vocabulary_size_comparison.png")

    ngrams = pd.DataFrame(ngram_rows)
    fig, axes = plt.subplots(2, 3, figsize=(14.0, 8.0))
    for row, class_name in enumerate(["Reliable", "Misleading"]):
        for col, n in enumerate([1, 2, 3]):
            subset = ngrams[(ngrams["Class"] == class_name) & (ngrams["n"] == n)].sort_values("count")
            axes[row, col].barh(subset["term"], subset["count"], color=COLORS[row])
            axes[row, col].set_title(f"{class_name} · {n}-gram")
            axes[row, col].set_xlabel("Frequency")
    fig.suptitle("Frequent unigrams, bigrams and trigrams (4,000 articles/class)", fontsize=14, fontweight="bold")
    finish(fig, "ngram_frequency_comparison.png")

    correlations = frame[["label", "word_count", "title_word_count", "sentence_count", "avg_sentence_length"]].corr()
    fig, ax = plt.subplots(figsize=(7.6, 6.0))
    sns.heatmap(correlations, annot=True, fmt=".2f", cmap="vlag", center=0, vmin=-1, vmax=1, ax=ax)
    ax.set_title(f"Correlation of engineered numerical features (n={len(frame):,})")
    finish(fig, "numerical_feature_correlation.png")

    subject = raw.groupby(["subject", "Class"]).size().reset_index(name="Rows")
    fig, ax = plt.subplots(figsize=(11.0, 5.4))
    sns.barplot(data=subject, x="subject", y="Rows", hue="Class", palette={"Reliable": COLORS[0], "Misleading": COLORS[1]}, ax=ax)
    ax.set_title(f"Subject distribution exposes a potential label shortcut (raw n={len(raw):,})")
    ax.set_xlabel("Original ISOT subject (excluded from model features)")
    ax.tick_params(axis="x", rotation=20)
    finish(fig, "subject_distribution.png")


if __name__ == "__main__":
    main()
