"""Transparent classification and summarization accountability report."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.config import FIGURES_DIR, REPORTS_DIR, RESULTS_DIR
from src.visualizations import model_comparison_chart
from ui import (
    callout,
    configure_page,
    footer,
    metric_strip,
    page_header,
    section_heading,
)


configure_page("NewsLens AI | Model Accountability", active="performance")
page_header(
    "Model Accountability Report",
    "Measured performance.\nVisible limitations.",
    "All values come from committed evaluation artifacts. Classification uses a held-out ISOT "
    "split after duplicate removal; summarization uses a fixed 150-article XSum test sample.",
)

metrics_path = RESULTS_DIR / "model_metrics.json"
comparison_path = REPORTS_DIR / "model_benchmark_results.csv"
benchmark_path = REPORTS_DIR / "model_benchmark_summary.json"
calibration_path = REPORTS_DIR / "calibration_validation.json"
summarization_path = RESULTS_DIR / "summarization_metrics.json"
classification_path = RESULTS_DIR / "classification_report.csv"

if not metrics_path.exists() or not comparison_path.exists() or not benchmark_path.exists():
    st.error("Evaluation files are missing. Run the private controlled benchmark workflow.")
    st.stop()

metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
comparison = pd.read_csv(comparison_path)
benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))

section_heading(
    "01 · Classification",
    "Champion-model results",
    "Macro-F1 gives both classes equal importance. ROC-AUC and PR-AUC evaluate ranking across "
    "thresholds; they do not by themselves prove calibration or cross-domain reliability.",
)
metric_strip(
    (
        ("Accuracy", f"{metrics['accuracy']:.4f}", "Overall held-out correctness"),
        ("Macro precision", f"{metrics['macro_precision']:.4f}", "Equal class weighting"),
        ("Macro recall", f"{metrics['macro_recall']:.4f}", "Equal class weighting"),
        ("Macro F1", f"{metrics['macro_f1']:.4f}", "Equal weight for both classes"),
        ("ROC-AUC", f"{metrics['roc_auc']:.4f}", "Threshold-independent ranking"),
    )
)

section_heading(
    "02 · Model Comparison",
    "Three controlled classical candidates",
    "Every candidate uses the same training, validation, and untouched final-test partitions. "
    "Confidence is calibrated separately with held-out validation rows.",
)
st.plotly_chart(
    model_comparison_chart(comparison),
    use_container_width=True,
    config={"displayModeBar": False, "responsive": True},
)
display_columns = [
    "model",
    "accuracy",
    "macro_precision",
    "macro_recall",
    "macro_f1",
    "roc_auc",
    "calibrated_brier_score",
    "calibrated_ece",
    "mean_inference_ms_per_article",
    "model_size_bytes",
]
st.dataframe(
    comparison[display_columns].style.format(
        {
            column: "{:.4f}"
            for column in [
                "accuracy",
                "macro_precision",
                "macro_recall",
                "macro_f1",
                "roc_auc",
                "calibrated_brier_score",
                "calibrated_ece",
                "mean_inference_ms_per_article",
            ]
        }
    ),
    use_container_width=True,
    hide_index=True,
)
callout(
    "Selection rationale",
    str(benchmark["selection"]["rationale"]),
    kind="success",
)

section_heading(
    "03 · Held-Out Diagnostics",
    "Error distribution and threshold behaviour",
    "The confusion matrix shows exact correct/error counts. ROC and precision-recall curves show "
    "ranking performance over thresholds on the same held-out split.",
)
left, right = st.columns(2, gap="large")
with left:
    image = FIGURES_DIR / "confusion_matrix.png"
    if image.exists():
        st.image(image, caption="Held-out confusion matrix", use_container_width=True)
    matrix = metrics.get("confusion_matrix", [[0, 0], [0, 0]])
    st.caption(
        f"Off-diagonal cells are dataset-label errors: {int(matrix[0][1])} false positives and "
        f"{int(matrix[1][0])} false negatives on the final test partition."
    )
with right:
    image = FIGURES_DIR / "roc_pr_curves.png"
    if image.exists():
        st.image(image, caption="ROC and precision-recall curves", use_container_width=True)
    st.caption("Near-perfect same-dataset curves may not transfer to unseen publishers or events.")

if classification_path.exists():
    class_report = pd.read_csv(classification_path)
    first_column = class_report.columns[0]
    class_report[first_column] = class_report[first_column].astype(str).replace(
        {"0": "Reliable", "1": "Misleading"}
    )
    section_heading(
        "04 · Class-Wise Performance",
        "Precision, recall, F1 and support",
        "Support is the number of held-out rows represented by each class or aggregate.",
    )
    st.dataframe(
        class_report.style.format(
            {
                "precision": "{:.4f}",
                "recall": "{:.4f}",
                "f1-score": "{:.4f}",
                "support": "{:.0f}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

section_heading(
    "05 · Calibration and Abstention",
    "Probability reliability and editorial review",
    "Platt scaling is fitted on validation-calibration rows. The review threshold is selected on a "
    "separate validation-policy subset and never tuned on the final test partition.",
)
metric_strip(
    (
        ("Brier score", f"{metrics['brier_score']:.4f}", "Lower is better"),
        ("Expected calibration error", f"{metrics['expected_calibration_error']:.4f}", "Ten equal-width bins"),
        (
            "Review threshold",
            f"{metrics['editorial_review_threshold']:.0%}",
            "Validation-policy selected",
        ),
        (
            "Final-test review rate",
            f"{benchmark['calibration']['test_editorial_review_rate']:.2%}",
            "Confidence rule only",
        ),
    )
)
reliability_image = FIGURES_DIR / "calibration_reliability.png"
if reliability_image.exists():
    st.image(
        reliability_image,
        caption="Reliability before and after Platt calibration on the untouched final test partition",
        use_container_width=True,
    )
callout(
    "Calibration boundary",
    "Calibration measures agreement between confidence and benchmark labels. It is not independent "
    "confirmation that an article is factually true or false.",
    kind="warning",
)

section_heading(
    "06 · Evaluation Protocol",
    "Partitioning, leakage controls and timing",
    "The fitted vocabulary and classifier remain inside one scikit-learn Pipeline. Exact duplicates "
    "are removed, two contaminated holdout rows are quarantined, and verified near-duplicate groups "
    "do not cross the final partitions.",
)
metric_strip(
    (
        ("Training rows", f"{metrics.get('train_samples', 0):,}", "Vectorizer fit only here"),
        ("Validation rows", f"{metrics.get('validation_samples', 0):,}", "Calibration and policy only"),
        ("Final test rows", f"{metrics.get('test_samples', 0):,}", "Untouched during fitting and policy selection"),
        (
            "Leakage audit",
            f"{benchmark['leakage_audit']['cross_partition_pairs_after_controls']} findings",
            "After duplicate controls",
        ),
        (
            "Inference latency",
            f"{metrics.get('mean_inference_ms_per_article', 0):.3f} ms",
            "Mean per held-out article",
        ),
    )
)

section_heading(
    "07 · Summarization",
    "Extractive ROUGE evaluation",
    "XSum references are highly abstractive and often one sentence long, making word-overlap "
    "metrics deliberately difficult for an extractive method.",
)
if summarization_path.exists():
    summary_metrics = json.loads(summarization_path.read_text(encoding="utf-8"))
    metric_strip(
        (
            ("ROUGE-1 F1", f"{summary_metrics['rouge1_f1']:.4f}", "Unigram overlap"),
            ("ROUGE-2 F1", f"{summary_metrics['rouge2_f1']:.4f}", "Bigram overlap"),
            ("ROUGE-L F1", f"{summary_metrics['rougeL_f1']:.4f}", "Longest-sequence overlap"),
            (
                "Mean compression",
                f"{summary_metrics['mean_compression_ratio_pct']:.1f}%",
                "Average word-count reduction",
            ),
            (
                "Mean latency",
                f"{summary_metrics['mean_latency_ms']:.1f} ms",
                f"{summary_metrics['sample_size']} XSum articles",
            ),
        )
    )
    callout(
        "Interpretation",
        str(summary_metrics.get("qualitative_note", "Human review remains necessary.")),
    )
else:
    st.info("Run `python training/evaluate_summarizer.py` to generate ROUGE results.")

callout(
    "Generalisation warning",
    "ISOT contains outlet, topic, period, and writing-style shortcuts. A high random-split score "
    "must not be interpreted as universal fact-checking accuracy.",
    kind="warning",
)
footer("NewsLens AI · Model Accountability", "Measured artifacts only · no fabricated metrics")
