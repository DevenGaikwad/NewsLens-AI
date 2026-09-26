"""Measured model-selection, calibration, and shortcut-resistance evidence."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.config import FIGURES_DIR, REPORTS_DIR
from ui import callout, configure_page, footer, metric_strip, page_header, section_heading


configure_page("NewsLens AI | Model Accountability", active="performance")
page_header(
    "Model Accountability · Locked Evidence",
    "A narrow model,\nmeasured honestly.",
    "All reported training articles and entities are synthetic. Selection, calibration, policy tuning, and final testing use separate event-grouped partitions.",
)
summary = json.loads((REPORTS_DIR / "model_benchmark_summary.json").read_text(encoding="utf-8"))
locked = summary["locked_final_test"]["metrics"]

metric_strip(
    (
        ("Accuracy", f"{locked['accuracy']:.3f}", "Locked final test"),
        ("Balanced accuracy", f"{locked['balanced_accuracy']:.3f}", "Equal-class average"),
        ("Macro F1", f"{locked['macro_f1']:.3f}", "Both synthetic labels"),
        ("Brier score", f"{locked['brier_score']:.8f}", "Platt calibrated"),
        ("ECE", f"{locked['expected_calibration_error']:.6f}", "10-bin estimate"),
        ("Automatic coverage", f"{locked['automatic_coverage']:.1%}", "Selected policy threshold"),
    )
)

section_heading("01 · Split Discipline", "Five partitions with event-group isolation", "Every paired synthetic event stays in one partition; content hashes do not cross partitions.")
partitions = summary["partitions"]
st.dataframe(pd.DataFrame([{"Partition": key.replace("_rows", "").replace("_", " ").title(), "Rows": value} for key, value in partitions.items() if key.endswith("_rows")]), hide_index=True, use_container_width=True)
callout("Leakage gate", f"Cross-partition event overlap: {partitions['cross_partition_event_overlap']}; content-hash overlap: {partitions['cross_partition_content_hash_overlap']}.", kind="success")

section_heading("02 · Candidate Selection", "Bounded model comparison", summary["selection"]["rationale"])
comparison = pd.read_csv(REPORTS_DIR / "model_benchmark_results.csv")
st.dataframe(comparison[["model", "accuracy", "balanced_accuracy", "macro_precision", "macro_recall", "macro_f1", "roc_auc", "pr_auc", "selected"]], hide_index=True, use_container_width=True)
st.image(FIGURES_DIR / "model_comparison.png", use_container_width=True)

section_heading("03 · Locked Evaluation", "Confusion and discrimination", "The 1,200-row final test was evaluated after candidate, calibration, and policy choices were fixed.")
left, right = st.columns(2, gap="large")
with left:
    st.image(FIGURES_DIR / "confusion_matrix.png", use_container_width=True)
with right:
    st.image(FIGURES_DIR / "roc_pr_curves.png", use_container_width=True)

section_heading("04 · Calibration and Abstention", "Hash-bound confidence", "Platt parameters name the exact model SHA-256. The policy partition selected the lowest threshold satisfying its declared accuracy and coverage rules.")
st.image(FIGURES_DIR / "calibration_reliability.png", use_container_width=True)
callout("Selected threshold", f"{summary['calibration']['editorial_review_threshold']:.2f}; final-test editorial-review rate {locked['editorial_review_rate']:.1%}.")

section_heading("05 · Shortcut and Counterfactual Controls", "Test the reason for the score", "Ordinary surface wording and metadata should not solve the paired ledger task.")
shortcuts = summary["shortcut_resistance"]
counterfactual = summary["counterfactual_evaluation"]
st.dataframe(pd.DataFrame([
    {"Control": "Surface text only", "Balanced accuracy": shortcuts["surface_text_only"]["balanced_accuracy"]},
    {"Control": "Metadata only", "Balanced accuracy": shortcuts["metadata_only"]["balanced_accuracy"]},
    {"Control": "Fact blocks removed", "Balanced accuracy": shortcuts["fact_block_ablation"]["balanced_accuracy"]},
    {"Control": "Account-block counterfactual", "Balanced accuracy": counterfactual["balanced_accuracy"]},
]), hide_index=True, use_container_width=True)
callout("Interpretation", f"Swapping only the Article account block changed {counterfactual['prediction_flip_rate']:.1%} of predictions and achieved {counterfactual['expected_label_accuracy']:.1%} expected-label accuracy.", kind="success")

callout("Generalisation warning", "Perfect in-distribution results reflect a deliberately structured synthetic comparison task. They do not establish real-world misinformation detection accuracy.", kind="warning")
footer("NewsLens AI · Model Accountability", "Synthetic-only · group-safe · locked evaluation")
