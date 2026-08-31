"""NewsLens AI editorial newsroom home page."""

from __future__ import annotations

import json

import streamlit as st

from src.config import MODEL_METADATA_PATH, RESULTS_DIR, ensure_runtime_directories
from src.database import initialize_database
from src.session_history import session_history_path
from ui import (
    callout,
    configure_page,
    editorial_strip,
    footer,
    hero,
    metric_strip,
    section_card,
    section_heading,
    workflow_steps,
)


configure_page("NewsLens AI | News Desk", active="home")
ensure_runtime_directories()
initialize_database(session_history_path())

metadata = {}
if MODEL_METADATA_PATH.exists():
    metadata = json.loads(MODEL_METADATA_PATH.read_text(encoding="utf-8"))
metrics = {}
metrics_path = RESULTS_DIR / "model_metrics.json"
if metrics_path.exists():
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

hero(
    "AI News Intelligence · Local and Explainable",
    "News\nintelligence,\nwith uncertainty\nintact.",
    "NewsLens AI condenses long-form reporting and independently estimates linguistic "
    "credibility risk from the original article. Every risk signal is accompanied by calibrated "
    "confidence, abstention, observed textual signals, responsible-use limits, and a private review archive.",
    technical_tags=(
        "TF-IDF classification",
        "Logistic Regression",
        "Article summarization",
        "Local explanations",
        "Validation-selected review",
        "Newsroom analytics and drift",
        "Session-isolated SQLite archive",
    ),
)

editorial_strip(
    (
        "Article Summarization",
        "TF-IDF Analysis",
        "Credibility Scoring",
        "Explainable AI",
        "Private Archive",
    )
)

metric_strip(
    (
        (
            "Champion model",
            metadata.get("champion_model", "TF-IDF + Logistic Regression"),
            "Saved pipeline · no runtime retraining",
        ),
        (
            "Final-test Macro F1",
            f"{metrics.get('macro_f1', 0):.3f}" if metrics else "Pending",
            "Untouched 2,399-row ISOT partition",
        ),
        ("Paid API", "Not required", "Hosting, compute, network and third-party terms may still apply"),
        ("Public history", "Session-only", "No cross-visitor archive sharing"),
    )
)

section_heading(
    "Methodology",
    "A two-layer news intelligence engine",
    "Summarization and classification answer different questions. They process the same "
    "validated article independently and are joined only when the editorial report is composed.",
)

methodology, flow = st.columns([1, 1.05], gap="large")
with methodology:
    section_card(
        "Readable compression",
        "The extractive summarizer ranks original sentences around a TF-IDF centroid. "
        "Optional DistilBART can produce new wording when its dependencies are installed.",
        label="Layer 01 · Summarization",
    )
    st.write("")
    section_card(
        "Credibility-risk estimation",
        "A saved TF-IDF and Logistic Regression pipeline examines the original cleaned article, "
        "produces a calibrated class probability, applies an abstention policy, and exposes signed "
        "contributions from observed terms.",
        label="Layer 02 · Classification",
    )
    callout(
        "Scientific separation",
        "The classifier never receives the generated summary. This prevents summarization from "
        "removing wording that may affect the risk estimate.",
        kind="success",
    )
with flow:
    workflow_steps(
        (
            ("Submit", "Paste text, provide a public URL, or upload a supported TXT/PDF file."),
            ("Extract", "Validate size and safety, recover article text, and preserve useful metadata."),
            ("Summarize", "Generate a Short, Medium, or Detailed reading view."),
            ("Classify", "Estimate lower/higher linguistic-risk direction from the cleaned source article."),
            ("Calibrate", "Apply Platt calibration and require human review below the validation threshold."),
            ("Explain", "Show calibrated confidence, local term contributions, timing, and limitations."),
            ("Review", "Record human evidence and export the session-isolated analysis."),
        )
    )

section_heading(
    "Capabilities",
    "Built for inspection, not spectacle",
    "Every page exposes a real project artifact or working operation. There are no placeholder "
    "metrics, decorative controls, or fabricated analysis results.",
)

first, second, third = st.columns(3, gap="large")
with first:
    section_card(
        "Analyse Article",
        "A focused editorial workspace for validated ingestion, summary generation, credibility "
        "verdicts, evidence signals, metadata, and downloadable reports.",
        label="Primary Desk",
    )
with second:
    section_card(
        "Model Accountability",
        "Measured classification and summarization results, class-wise diagnostics, model "
        "comparison, held-out charts, timing, and plain-language interpretation.",
        label="Transparency",
    )
with third:
    section_card(
        "Dataset & Archive",
        "Research-style EDA discloses leakage risks, while the private archive supports "
        "human review, aggregate analytics, drift readiness, exporting, and confirmed deletion.",
        label="Evidence Record",
    )

callout(
    "Important boundary",
    "NewsLens AI estimates similarity to writing patterns in its training data. It does not "
    "retrieve independent evidence or prove that an individual claim is true or false.",
    kind="warning",
)

footer(
    "NewsLens AI · Local-first research software",
    "Saved TF-IDF + Logistic Regression · Responsible-use boundaries",
)
