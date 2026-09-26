"""Research grounding, architecture, privacy, limitations, and project details."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.config import COPYRIGHT_NOTICE, DISCLAIMER, MODEL_METADATA_PATH, PROJECT_AUTHOR, PROJECT_ROOT
from src.report_exporter import archive_csv_bytes
from ui import callout, configure_page, footer, metadata_grid, page_header, section_card, section_heading, workflow_steps


configure_page("NewsLens AI | Research & About", active="about")
page_header(
    "Research & About",
    "A transparent academic\nnews-intelligence prototype.",
    "NewsLens AI combines deterministic summarization with a narrow synthetic consistency classifier, calibrated confidence, human review, privacy-safe analytics, and explicit responsible-use boundaries.",
)
metadata = json.loads(MODEL_METADATA_PATH.read_text(encoding="utf-8")) if MODEL_METADATA_PATH.exists() else {}

section_heading("01 · Purpose", "Readable text plus inspectable consistency", "The summary helps a reader navigate text. The classifier answers only whether two visible fictional ledgers agree.")
left, right = st.columns(2, gap="large")
with left:
    section_card("Article overload", "Local extractive summarization selects original sentences without an external generative checkpoint.", label="Need 01")
with right:
    section_card("Opaque outputs", "Calibrated probabilities, abstention, match/mismatch tokens, hashes, and reports make the narrow model inspectable.", label="Need 02")

section_heading("02 · Architecture", "Seven implemented runtime stages", "Training is offline and is never triggered by application startup.")
workflow_steps((
    ("Presentation", "Responsive Streamlit pages, charts, and exports."),
    ("Ingestion", "Paste, public URL, TXT/PDF, validation, and safe extraction."),
    ("Summary", "Deterministic TF-IDF centroid sentence selection."),
    ("Signals", "Visible Reference note and Article account parsing."),
    ("Classifier", "Synthetic-trained TF-IDF and Logistic Regression."),
    ("Policy", "Model-bound Platt calibration and abstention."),
    ("Archive", "Session-isolated review records and aggregate monitoring."),
))

section_heading("03 · Public Artifacts", "Synthetic model and calibration binding", "Every public artifact records the accepted dataset identity and the calibration names the exact model SHA-256.")
metadata_grid((
    ("Model", metadata.get("artifact_id", "Unavailable")),
    ("Model type", metadata.get("model_type", "Unavailable")),
    ("Training articles", f"{metadata.get('training_articles', 0):,}"),
    ("Dataset", metadata.get("dataset_id", "Unavailable")),
    ("Synthetic only", str(metadata.get("synthetic_only", False))),
    ("Private ISOT content used", str(metadata.get("private_isot_content_used", True))),
))

section_heading("04 · Responsible AI", "Capabilities and explicit limits", "The interface uses consistency language because classification is not evidence retrieval or factual verification.")
can_do, cannot_do = st.columns(2, gap="large")
with can_do:
    st.markdown("""### What the system can do

1. Compress an article into a local reading view.
2. Compare visible fields in the supported synthetic format.
3. Expose influential observed and derived terms.
4. Report calibrated confidence and abstain outside scope.
5. Preserve a private, session-local human review record.
""")
with cannot_do:
    st.markdown("""### What the system cannot do

1. Verify real claims against primary evidence.
2. Judge an ordinary article without the paired ledger format.
3. Infer intent, political truth, or source reputation.
4. Claim general fake-news detection performance.
5. Replace journalists, researchers, or fact-checkers.
""")
callout("Important disclaimer", DISCLAIMER, kind="warning")

section_heading("05 · Privacy", "Safe for a public demonstration", "No paid AI API is required; uploaded files and full article text are not persisted by the public session workflow.")
metadata_grid((("Uploaded files", "Parsed in memory; not stored"), ("Original article", "Not persisted in SQLite"), ("Public history", "Per-session and temporary"), ("URL requests", "Only when explicitly submitted"), ("Training archive", "Not exposed through the application")))

section_heading("06 · Literature", "Research-survey matrix", "The matrix covers summarization, explainability, dataset bias, calibration, and cross-domain limitations. Citations are background, not training data.")
papers_path = PROJECT_ROOT / "docs" / "research_papers.json"
if papers_path.exists():
    frame = pd.DataFrame(json.loads(papers_path.read_text(encoding="utf-8")))
    with st.expander("Open the literature matrix"):
        st.dataframe(frame, hide_index=True, use_container_width=True)
    st.download_button("Download Literature Matrix as CSV", archive_csv_bytes(frame), file_name="research_paper_matrix.csv", mime="text/csv")

section_heading("07 · Ownership and Academic Integrity", "Source-visible demonstration", "Original project components remain proprietary and All Rights Reserved; dataset licensing is documented separately.")
metadata_grid((("Project", "NewsLens AI"), ("Author and developer", PROJECT_AUTHOR), ("Copyright", COPYRIGHT_NOTICE), ("Permission model", "Proprietary source-visible application")))
callout("Publication status", "The synthetic model, bound calibration, and evidence package are intended for public demonstration. No ISOT content or private ISOT-derived artifact is included.", kind="success")
footer("NewsLens AI · Research & About", "Authorship · evidence · responsible scope")
