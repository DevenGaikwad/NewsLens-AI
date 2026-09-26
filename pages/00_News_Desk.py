"""NewsLens AI editorial newsroom home page."""

from __future__ import annotations

import json

import streamlit as st

from src.config import MODEL_METADATA_PATH, RESULTS_DIR, ensure_runtime_directories
from src.database import initialize_database
from src.session_history import session_history_path
from ui import callout, configure_page, editorial_strip, footer, hero, metric_strip, section_card, section_heading, workflow_steps


configure_page("NewsLens AI | News Desk", active="home")
ensure_runtime_directories()
initialize_database(session_history_path())

metadata = json.loads(MODEL_METADATA_PATH.read_text(encoding="utf-8")) if MODEL_METADATA_PATH.exists() else {}
metrics_path = RESULTS_DIR / "model_metrics.json"
metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}

hero(
    "Synthetic News Intelligence · Local and Explainable",
    "News\nintelligence,\nwith scope\nintact.",
    "NewsLens AI creates a deterministic reading summary and evaluates whether two visible, "
    "fictional ledger descriptions agree. The public classifier and its calibration were trained "
    "only from an independently authored synthetic benchmark.",
    technical_tags=(
        "Synthetic-only training", "TF-IDF + Logistic Regression", "Platt calibration",
        "Transparent abstention", "Local explanations", "Session-isolated archive",
    ),
)
editorial_strip(("Local Summarization", "Synthetic Ledger Comparison", "Calibration", "Explainability", "Private Archive"))

metric_strip(
    (
        ("Training articles", f"{metadata.get('training_articles', 0):,}", "Synthetic training partition"),
        ("Locked-test Macro F1", f"{metrics.get('macro_f1', 0):.3f}" if metrics else "Pending", "1,200-row final test"),
        ("Calibration ECE", f"{metrics.get('expected_calibration_error', 0):.6f}" if metrics else "Pending", "Lower is better"),
        ("Paid API", "Not required", "CPU-friendly local workflow"),
    )
)

section_heading(
    "Methodology",
    "Two transparent, bounded paths",
    "Summarization improves readability. Classification compares the visible Reference note and "
    "Article account fields. Neither path verifies real-world claims.",
)
left, right = st.columns([1, 1.05], gap="large")
with left:
    section_card(
        "Readable compression",
        "The deterministic extractive summarizer ranks and returns original sentences. It uses no external checkpoint or paid service.",
        label="Path 01 · Summary",
    )
    st.write("")
    section_card(
        "Synthetic consistency",
        "The saved linear pipeline derives field-level match or mismatch tokens, applies Platt calibration, and can abstain outside its supported format.",
        label="Path 02 · Classifier",
    )
with right:
    workflow_steps(
        (
            ("Submit", "Paste text, fetch a public URL, or upload TXT/PDF."),
            ("Summarize", "Build a local extractive reading view."),
            ("Compare", "Parse the two visible fictional fact ledgers."),
            ("Calibrate", "Bind confidence to the published model hash."),
            ("Review", "Abstain when required and retain a session-local record."),
        )
    )

callout(
    "Scope boundary",
    "This demonstration recognizes authored synthetic consistency patterns. It is not a general fake-news detector, source reputation service, or factual verification system.",
    kind="warning",
)
footer("NewsLens AI · News Desk", "Synthetic-only classifier · deterministic summary")
