"""Research grounding, architecture, privacy, limitations, and project details."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.config import (
    COPYRIGHT_NOTICE,
    DISCLAIMER,
    MODEL_METADATA_PATH,
    PROJECT_AUTHOR,
    PROJECT_ROOT,
)
from src.report_exporter import archive_csv_bytes
from ui import (
    callout,
    configure_page,
    footer,
    metadata_grid,
    page_header,
    section_card,
    section_heading,
    workflow_steps,
)


configure_page("NewsLens AI | Research & About", active="about")
page_header(
    "Research & About",
    "A transparent academic\nnews-intelligence prototype.",
    "NewsLens AI combines robust article ingestion, two independent NLP branches, explainable "
    "classification, calibrated confidence, human review, local analytics, drift readiness, and "
    "explicit responsible-use boundaries.",
)

metadata = {}
if MODEL_METADATA_PATH.exists():
    metadata = json.loads(MODEL_METADATA_PATH.read_text(encoding="utf-8"))

section_heading(
    "01 · Purpose",
    "The problem being addressed",
    "Readers need concise access to long articles and a cautious indication of linguistic "
    "credibility risk. These are related needs, but they are not the same scientific task.",
)
purpose_left, purpose_right = st.columns(2, gap="large")
with purpose_left:
    section_card(
        "Article overload",
        "Extractive or optional abstractive summarization creates a shorter reading view while "
        "preserving the full article as the independent classifier input.",
        label="Need 01",
    )
with purpose_right:
    section_card(
        "Opaque model outputs",
        "Calibrated probabilities, abstention, observed term contributions, measured limitations, "
        "and downloadable records make the risk signal inspectable.",
        label="Need 02",
    )

section_heading(
    "02 · Architecture",
    "Six implemented runtime stages",
    "The Streamlit presentation layer orchestrates small reusable modules. Training remains an "
    "offline workflow and is never triggered by application startup.",
)
workflow_steps(
    (
        ("Presentation", "Editorial Streamlit pages, responsive navigation, Plotly charts, and exports."),
        ("Ingestion", "Direct text, public URL, TXT/PDF parsing, validation, and safe extraction."),
        ("NLP preparation", "Conservative cleaning, sentence segmentation, metadata, and language hint."),
        ("AI processing", "TF-IDF centroid/DistilBART summary plus saved TF-IDF Logistic Regression."),
        ("Risk policy", "Platt calibration, a validation-selected abstention threshold, and scope checks."),
        ("Human review", "Session-local evidence notes, source URLs, status, and final assessment."),
        ("Monitoring", "Privacy-safe newsroom analytics and lightweight distribution-drift indicators."),
    )
)

section_heading(
    "03 · Methodology",
    "AI and machine-learning methods",
    "The classifier and summarizer receive the same original cleaned article but remain "
    "scientifically independent until their outputs are displayed together.",
)
method_one, method_two, method_three = st.columns(3, gap="large")
with method_one:
    section_card(
        "TF-IDF representation",
        "Word unigrams and bigrams are weighted by within-document frequency and cross-corpus rarity.",
        label="Text Features",
    )
with method_two:
    section_card(
        "Logistic Regression",
        "A linear classifier maps sparse text features to lower/higher linguistic-risk directions.",
        label="Risk Model",
    )
with method_three:
    section_card(
        "Local explanation",
        "Observed TF-IDF values are multiplied by learned coefficients to expose signed term contributions.",
        label="Explainability",
    )

section_heading(
    "04 · Technology",
    "Portable Python-first stack",
    "The core workflow requires no paid API. Hosting, network, compute, and third-party terms may "
    "still carry costs. Optional DistilBART downloads once and then reuses the local Hugging Face cache.",
)
metadata_grid(
    (
        ("Application", "Streamlit multipage UI"),
        ("Data", "pandas · NumPy"),
        ("Machine learning", "scikit-learn · Joblib"),
        ("Visualisation", "Plotly · Matplotlib · Seaborn"),
        ("Extraction", "Requests · Trafilatura · BeautifulSoup"),
        ("Documents", "pypdf · ReportLab"),
        ("Persistence", "Session-isolated SQLite"),
        ("Testing", "pytest · Streamlit AppTest · Playwright QA"),
        ("Saved classifier", metadata.get("champion_model", "TF-IDF + Logistic Regression")),
        ("Interface", "Warm editorial newsroom"),
    )
)

section_heading(
    "05 · Responsible AI",
    "Capabilities and explicit limits",
    "The interface uses risk language because linguistic classification is not evidence retrieval or factual verification.",
)
can_do, cannot_do = st.columns(2, gap="large")
with can_do:
    st.markdown(
        """
### What the system can do

1. Compress a long article into a selectable reading view.
2. Estimate similarity to training-dataset writing patterns.
3. Expose influential observed TF-IDF terms.
4. Report calibrated confidence and abstain when review is required.
5. Preserve a human editorial review in a private session record.
6. Summarise session-local analytics and drift readiness without retraining.
"""
    )
with cannot_do:
    st.markdown(
        """
### What the system cannot do

1. Verify individual claims against independent primary evidence.
2. Reliably cover every publisher, language, satire style, or breaking event.
3. Infer author intent, political truth, or source trust from wording alone.
4. Guarantee fairness across regions, topics, ideologies, or time periods.
5. Replace journalists, researchers, or professional fact-checkers.
"""
    )
callout("Important disclaimer", DISCLAIMER, kind="warning")

section_heading(
    "06 · Privacy and Data Handling",
    "Safe for local and public demonstration",
    "The core application does not call a paid AI API, does not permanently retain uploaded files, "
    "and separates each public visitor's archive into a private temporary database.",
)
metadata_grid(
    (
        ("Uploaded files", "Parsed in memory; not stored"),
        ("Original article", "Not persisted in SQLite"),
        ("Review notes and sources", "Current visitor's scoped SQLite only"),
        ("Public history", "Per-session SQLite; temporary across cloud restarts"),
        ("Trusted local history", "Optional persistent mode for a single user"),
        ("URL requests", "Only when the user submits a public URL"),
        ("Transformer network use", "Optional first model download only"),
        ("Deletion", "User-confirmed record or archive removal"),
    )
)

section_heading(
    "07 · Literature",
    "Verified research-survey matrix",
    "The matrix covers summarization, fake-news classification, explainability, automated "
    "fact-checking, dataset bias, and cross-domain generalisation.",
)
papers_path = PROJECT_ROOT / "docs" / "research_papers.json"
if papers_path.exists():
    papers = json.loads(papers_path.read_text(encoding="utf-8"))
    frame = pd.DataFrame(papers)
    visible = [
        column
        for column in [
            "Sr. No.",
            "Paper title",
            "Authors",
            "Year",
            "Publisher/conference/journal",
            "Access status",
            "Relevance to this project",
        ]
        if column in frame.columns
    ]
    with st.expander("Open the complete literature matrix"):
        st.dataframe(frame[visible], hide_index=True, use_container_width=True)
    st.download_button(
        "Download Literature Matrix as CSV",
        archive_csv_bytes(frame),
        file_name="research_paper_matrix.csv",
        mime="text/csv",
    )
else:
    st.info("The research matrix will appear here after the documentation build.")

st.markdown(
    """
### Conceptual implementations reviewed

1. [Summarize News Articles with Machine Learning in Python](https://youtu.be/z4DQYprjPSs) — article-ingestion and summarization reference.
2. [Fake News Detection in Python](https://youtu.be/ZE2DANLfBIs) — TF-IDF and classical-classification reference.

NewsLens AI re-engineers those tutorial-scale ideas into original modules, a saved pipeline,
local explanations, safe ingestion, SQLite history, reproducible evaluation, and a consistent
multipage interface.
"""
)

section_heading(
    "08 · Ownership and Academic Integrity",
    "Publicly viewable does not mean freely reusable",
    "NewsLens AI is prepared for public source publication for demonstration, portfolio review, "
    "and academic evaluation. "
    "Its original components remain proprietary and All Rights Reserved.",
)
metadata_grid(
    (
        ("Project", "NewsLens AI"),
        ("Author and developer", PROJECT_AUTHOR),
        ("Copyright", COPYRIGHT_NOTICE),
        ("Permission model", "Proprietary source-visible; not open source"),
    )
)
st.markdown(
    """
### Academic-integrity boundary

1. Public availability is not permission to submit NewsLens AI, or a derivative, as somebody else's academic or professional project.
2. Research or academic use should cite NewsLens AI and Deven Sachin Gaikwad.
3. Third-party packages, datasets, research papers, and checkpoints retain their own rights and acknowledgements.
4. The classifier estimates linguistic credibility risk from learned language patterns; it does not prove factual truth.
"""
)

section_heading(
    "09 · Project Record",
    "Prepared for reproducible review",
    "The source package includes code, a privately retained model artifact, tests, diagrams, measured "
    "outputs, current screenshots, research records, setup guidance, and release-audit evidence.",
)
callout(
    "Publication gate",
    "The trained classifier remains excluded from public staging until documentary redistribution "
    "rights are established. Removing it makes the classifier unavailable, so public deployment remains blocked.",
    kind="warning",
)
footer("NewsLens AI · Research & About", "Authorship · evidence · responsible use")
