"""Publication-style dataset profile, EDA, and leakage-risk disclosure."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import FIGURES_DIR, RESULTS_DIR
from ui import (
    callout,
    configure_page,
    footer,
    metric_strip,
    page_header,
    section_heading,
)


def figure_panel(path: Path, title: str, interpretation: str) -> None:
    st.markdown(f"### {title}")
    if path.exists():
        st.image(path, use_container_width=True)
    else:
        st.info(f"Figure unavailable: {path.name}")
    st.caption(interpretation)


configure_page("NewsLens AI | Dataset Analysis", active="eda")
page_header(
    "Dataset Analysis · Research Appendix",
    "Know the collection\nbefore trusting the score.",
    "This report documents class balance, cleaning outcomes, language patterns, duplicates, "
    "source-marker mitigation, and the remaining limitations of ISOT-based classification.",
)

profile_path = RESULTS_DIR / "dataset_profile.json"
if not profile_path.exists():
    st.error("Dataset profile is missing. Run the training script first.")
    st.stop()
profile = json.loads(profile_path.read_text(encoding="utf-8"))

section_heading(
    "01 · Dataset Overview",
    "From raw collection to modelling sample",
    "Rows were screened for minimum content, deduplicated before splitting, and sampled evenly "
    "for the reproducible 24,000-row development dataset.",
)
metric_strip(
    (
        ("Raw articles", f"{profile['raw_rows']:,}", "True.csv + Fake.csv"),
        ("Clean rows", f"{profile['clean_rows']:,}", "After filtering and deduplication"),
        ("Duplicates removed", f"{profile['duplicates_removed']:,}", "Exact normalized-text hashes"),
        ("Sample reliable", f"{profile['reliable_rows']:,}", "Balanced modelling rows"),
        ("Sample misleading", f"{profile['misleading_rows']:,}", "Balanced modelling rows"),
    )
)

section_heading(
    "02 · Core Distributions",
    "Class balance and article length",
    "Balanced modelling prevents majority-class dominance. Length differences are disclosed "
    "because they can become accidental predictive shortcuts.",
)
left, right = st.columns(2, gap="large")
with left:
    figure_panel(
        FIGURES_DIR / "class_distribution.png",
        "2.1 Class distribution",
        "The working sample is exactly balanced, so accuracy is not inflated by class prevalence.",
    )
with right:
    figure_panel(
        FIGURES_DIR / "word_count_distribution.png",
        "2.2 Article-length distribution",
        "Class-specific length profiles reflect collection and editorial differences, not factual truth.",
    )

section_heading(
    "03 · Language and Vocabulary",
    "Repeated terms, n-grams and model coefficients",
    "These views reveal what the corpus and linear model notice. Strong publisher-, topic-, or "
    "date-related terms are warnings about shortcut learning.",
)
third, fourth = st.columns(2, gap="large")
with third:
    figure_panel(
        FIGURES_DIR / "top_ngrams.png",
        "3.1 Frequent unigrams",
        "High-frequency words differ between source collections and can encode topic or outlet style.",
    )
with fourth:
    figure_panel(
        FIGURES_DIR / "feature_importance.png",
        "3.2 Global model coefficients",
        "Coefficient magnitude indicates model influence; it is not evidence that a term is truthful or deceptive.",
    )

fifth, sixth = st.columns(2, gap="large")
with fifth:
    figure_panel(
        FIGURES_DIR / "vocabulary_size_comparison.png",
        "3.3 Vocabulary-size comparison",
        "Equal 4,000-article samples make vocabulary breadth comparable across labels.",
    )
with sixth:
    figure_panel(
        FIGURES_DIR / "ngram_frequency_comparison.png",
        "3.4 Unigram, bigram and trigram comparison",
        "Multiword phrases expose topic, period, and editorial conventions learned from the collection.",
    )

section_heading(
    "04 · Quality and Leakage Audit",
    "Missingness, duplicates and engineered indicators",
    "The audit separates genuine data-quality controls from risks that cannot be fully removed "
    "without external publishers, time periods, and domains.",
)
seventh, eighth = st.columns(2, gap="large")
with seventh:
    figure_panel(
        FIGURES_DIR / "missing_values_heatmap.png",
        "4.1 Missing-value audit",
        "Raw missingness is recorded; short or unusable article bodies are handled as a separate quality rule.",
    )
with eighth:
    figure_panel(
        FIGURES_DIR / "duplicate_record_analysis.png",
        "4.2 Duplicate and eligibility audit",
        "Exact duplicates are removed before any train/test split, preventing direct row leakage.",
    )

ninth, tenth = st.columns(2, gap="large")
with ninth:
    figure_panel(
        FIGURES_DIR / "title_length_distribution.png",
        "4.3 Title-length distribution",
        "Title length correlates with collection style and must not be interpreted as a truth signal.",
    )
with tenth:
    figure_panel(
        FIGURES_DIR / "average_sentence_length.png",
        "4.4 Average sentence length",
        "Sentence structure differs across source collections and may contribute to style-based prediction.",
    )

eleventh, twelfth = st.columns(2, gap="large")
with eleventh:
    figure_panel(
        FIGURES_DIR / "numerical_feature_correlation.png",
        "4.5 Numerical-feature correlations",
        "Correlation identifies association, not causal evidence of misinformation.",
    )
with twelfth:
    figure_panel(
        FIGURES_DIR / "subject_distribution.png",
        "4.6 Subject distribution",
        "Subject values are nearly label-specific, so the subject field is excluded from model features.",
    )

section_heading(
    "05 · Dataset Selection",
    "Why ISOT was used—and what it cannot establish",
    "ISOT provides full article text and a simple reproducible download, but source and topic "
    "separation can make same-dataset evaluation optimistic.",
)
comparison = pd.DataFrame(
    [
        [
            "ISOT",
            "44,898 full articles",
            "Binary",
            "Direct CSV download",
            "Selected; large and reproducible, with disclosed source leakage risk",
        ],
        [
            "LIAR",
            "12,836 short claims",
            "Six-way",
            "Public ACL resource",
            "Strong labels; input format does not match long-form article analysis",
        ],
        [
            "FakeNewsNet",
            "News + social context",
            "Binary",
            "Collection scripts / APIs",
            "Rich context; availability and reproducibility friction",
        ],
    ],
    columns=["Dataset", "Scale / content", "Labels", "Access", "Decision"],
)
st.dataframe(comparison, hide_index=True, use_container_width=True)

section_heading(
    "06 · Controls and Limits",
    "Leakage mitigations implemented",
    "These controls reduce obvious shortcuts but cannot turn one historical collection into a "
    "representative sample of every publisher, region, language, event, or time period.",
)
st.markdown(
    """
1. Exact normalized article hashes are deduplicated before splitting.
2. Title and body are combined, while publisher/source identity and subject are excluded.
3. Reuters/byline/source markers are neutralised in training and inference.
4. TF-IDF is fitted inside the scikit-learn Pipeline on training folds only.
5. The train/test split is stratified with seed 42; the held-out set remains untouched during selection.
6. Every performance surface carries the remaining domain-shift warning.
"""
)
callout(
    "Known ISOT limitation",
    "Reliable-labelled stories are largely Reuters reports, while misleading-labelled stories come "
    "from different outlets. Removing explicit markers reduces but cannot erase publisher, topic, "
    "period, and writing-style signatures.",
    kind="warning",
)
footer("NewsLens AI · Dataset Analysis", "Research appendix · measured artifacts")
