"""End-to-end editorial article analysis workspace."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

import streamlit as st

from src.abstractive_summarizer import (
    AbstractiveDependencyError,
    load_transformer_pipeline,
    summarize_abstractive,
)
from src.article_extractor import ArticleData, ArticleExtractionError, extract_article
from src.config import (
    DISCLAIMER,
    HIGHER_RISK_OUTCOME,
    LOWER_RISK_OUTCOME,
    MIN_ARTICLE_WORDS,
)
from src.database import insert_analysis
from src.extractive_summarizer import summarize_extractive
from src.fake_news_predictor import ModelLoadError, load_model, predict_credibility
from src.file_parser import FileParseError, parse_uploaded_file, safe_upload_filename
from src.model_diagnostics import assess_input
from src.report_exporter import analysis_json_bytes, analysis_pdf_bytes
from src.session_history import session_history_path
from src.text_preprocessor import clean_article_text, split_sentences
from src.utils import article_hash, domain_from_url, reading_time_minutes, utc_now_iso, word_count
from src.visualizations import confidence_gauge, feature_contribution_chart
from ui import (
    callout,
    configure_page,
    editorial_strip,
    evidence_terms,
    footer,
    metadata_grid,
    metric_strip,
    page_header,
    reading_panel,
    result_status,
    section_heading,
)


configure_page("NewsLens AI | Analyse Article", active="analyse")
page_header(
    "Primary Analysis Desk",
    "Analyse one article.\nInspect two independent AI views.",
    "Summarization creates a compact reading view. Credibility classification examines the "
    "original cleaned article and reports a cautious, explainable risk estimate.",
)
editorial_strip(("Submit", "Extract", "Summarize", "Classify", "Explain", "Archive"))


@st.cache_resource(show_spinner="Loading the saved credibility-risk model…")
def cached_model():
    return load_model()


@st.cache_resource(show_spinner="Loading the optional DistilBART model…")
def cached_abstractive_model():
    return load_transformer_pipeline()


def verdict_interpretation(label: str, confidence_band: str, review_reason: str = "") -> str:
    if label == LOWER_RISK_OUTCOME:
        message = "The article more closely resembles lower-risk linguistic patterns in the training data."
    elif label == HIGHER_RISK_OUTCOME:
        message = "The article more closely resembles higher-risk linguistic patterns in the training data."
    else:
        message = "The system abstained from an automatic directional outcome."
        if review_reason:
            message = f"{message} {review_reason}"
    return f"{message} Confidence band: {confidence_band}. Independent editorial verification remains necessary."


section_heading(
    "01 · Prepare",
    "Article source and analysis settings",
    "Choose a source, summary method, and reading length. The classifier path is fixed to the "
    "saved model and always receives the original cleaned article.",
)

settings_one, settings_two = st.columns([1.35, 1], gap="large")
with settings_one:
    summary_method = st.selectbox(
        "Summarization method",
        ["Extractive · TF-IDF centroid", "Abstractive · DistilBART (optional)"],
        help="Extractive mode is fast and offline. Abstractive mode requires transformers and torch.",
    )
with settings_two:
    summary_length = st.radio(
        "Summary length",
        ["Short", "Medium", "Detailed"],
        horizontal=True,
        help="Controls the target size of the generated reading view.",
    )

input_method = st.radio(
    "Article source",
    ["Paste text", "Public URL", "TXT / PDF upload"],
    horizontal=True,
)

article_text = ""
article_title = "Untitled article"
source_url = ""
source_domain = ""
author = "Not available"
publication_date = "Not available"
extractor = "Direct input"
uploaded = None

if input_method == "Paste text":
    article_title = (
        st.text_input("Article title (optional)", placeholder="Enter a concise descriptive title")
        or article_title
    )
    sample_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "sample"
        / "reliable_style_article.txt"
    )
    sample_value = str(st.session_state.get("loaded_sample", ""))
    article_text = st.text_area(
        "Full article text",
        value=sample_value,
        height=310,
        placeholder=f"Paste at least {MIN_ARTICLE_WORDS} words of article text…",
    )
    sample_col, clear_col, _ = st.columns([1, 1, 3])
    if sample_col.button("Load Packaged Sample", use_container_width=True) and sample_path.exists():
        st.session_state["loaded_sample"] = sample_path.read_text(encoding="utf-8")
        st.rerun()
    if clear_col.button("Clear Text", use_container_width=True, disabled=not bool(sample_value)):
        st.session_state.pop("loaded_sample", None)
        st.rerun()
elif input_method == "Public URL":
    source_url = st.text_input(
        "Public article URL",
        placeholder="https://example.com/news/article",
        help="Only public HTTP(S) addresses are accepted. Local and private network targets are blocked.",
    )
    callout(
        "Extraction note",
        "Paywalled, script-only, consent-gated, and anti-bot websites may not expose readable article text.",
    )
else:
    uploaded = st.file_uploader(
        "Upload a TXT or text-based PDF",
        type=["txt", "pdf"],
        help="Maximum size: 10 MB. Scanned PDFs require OCR and are not supported by the core parser.",
    )

analyse_clicked = st.button("Analyse Article", type="primary", use_container_width=True)

if analyse_clicked:
    st.session_state["analysis_attempts_total"] = int(
        st.session_state.get("analysis_attempts_total", 0)
    ) + 1
    started = perf_counter()
    try:
        if input_method == "Public URL":
            extracted: ArticleData = extract_article(source_url)
            article_text = extracted.text
            article_title = extracted.title
            author = extracted.author
            publication_date = extracted.publication_date
            source_url = extracted.source_url
            source_domain = extracted.source_domain
            extractor = extracted.extractor
        elif input_method == "TXT / PDF upload":
            if uploaded is None:
                raise FileParseError("Choose a TXT or PDF file before starting the analysis.")
            article_title = safe_upload_filename(uploaded.name)
            article_text = parse_uploaded_file(article_title, uploaded.getvalue())
            extractor = "TXT/PDF parser"

        cleaned = clean_article_text(article_text, remove_source_markers=False)
        original_words = word_count(cleaned)
        if original_words < MIN_ARTICLE_WORDS:
            raise ValueError(
                f"Enter at least {MIN_ARTICLE_WORDS} words for a meaningful analysis."
            )
        if not source_domain:
            source_domain = domain_from_url(source_url)

        with st.spinner("Running independent summarization and credibility-risk pipelines…"):
            model = cached_model()
            diagnostics = assess_input(cleaned, model)
            if summary_method.startswith("Abstractive"):
                summarizer = cached_abstractive_model()
                summary = summarize_abstractive(cleaned, summarizer, summary_length)
            else:
                summary = summarize_extractive(cleaned, summary_length)
            prediction = predict_credibility(
                cleaned,
                model,
                diagnostics=diagnostics,
            )

        total_time = perf_counter() - started
        record = {
            "timestamp": utc_now_iso(),
            "input_type": input_method,
            "source_url": source_url,
            "source_domain": source_domain,
            "article_title": article_title,
            "article_hash": article_hash(cleaned),
            "original_word_count": original_words,
            "summary_method": summary.method,
            "summary_length": summary_length,
            "generated_summary": summary.summary,
            "prediction_label": prediction.display_label,
            "predicted_class": prediction.predicted_class,
            "reliable_probability": prediction.reliable_probability,
            "misleading_probability": prediction.misleading_probability,
            "calibrated_confidence": prediction.confidence,
            "confidence_band": prediction.confidence_band,
            "calibration_method": prediction.calibration_method,
            "editorial_review_threshold": prediction.editorial_review_threshold,
            "review_required": int(prediction.review_required),
            "review_reason": prediction.review_reason,
            "review_status": "Pending review",
            "reviewer_notes": "",
            "supporting_source_urls": "",
            "final_editorial_assessment": "",
            "review_updated_at": None,
            "vocabulary_coverage": diagnostics.vocabulary_coverage,
            "oov_rate": diagnostics.out_of_vocabulary_rate,
            "language_mismatch": int(diagnostics.language_mismatch),
            "domain_mismatch": int(diagnostics.domain_mismatch),
            "model_version": prediction.model_version,
            "processing_time": round(total_time, 4),
        }
        analysis_id, duplicate = insert_analysis(record, path=session_history_path())
        sentences = split_sentences(cleaned)
        payload = {
            **record,
            "analysis_id": analysis_id,
            "author": author,
            "publication_date": publication_date,
            "extractor": extractor,
            "reading_time_minutes": reading_time_minutes(cleaned),
            "language_hint": diagnostics.language_hint,
            "sentence_count": len(sentences),
            "average_sentence_words": round(original_words / max(1, len(sentences)), 1),
            "summary_word_count": summary.summary_word_count,
            "compression_ratio_pct": summary.compression_ratio_pct,
            "summarization_time": summary.processing_time_seconds,
            "classification_time": prediction.processing_time_seconds,
            "confidence": prediction.confidence,
            "calibration_status": prediction.calibration_status,
            "input_diagnostics": diagnostics.to_dict(),
            "explanation": prediction.explanation,
        }
        st.session_state["last_analysis"] = payload
        st.session_state["last_duplicate"] = duplicate
    except (ArticleExtractionError, FileParseError, ModelLoadError, AbstractiveDependencyError, ValueError) as exc:
        st.session_state["analysis_attempts_invalid"] = int(
            st.session_state.get("analysis_attempts_invalid", 0)
        ) + 1
        st.error(str(exc))
    except Exception:
        st.session_state["analysis_attempts_invalid"] = int(
            st.session_state.get("analysis_attempts_invalid", 0)
        ) + 1
        st.error("Unable to complete the analysis. Check the input and installation, then try again.")

payload = st.session_state.get("last_analysis")
if payload:
    section_heading(
        "02 · Analysis Complete",
        str(payload["article_title"]),
        f"Structured report #{payload['analysis_id']} · {payload['timestamp']}",
    )
    if st.session_state.get("last_duplicate"):
        callout(
            "Existing archive record",
            f"This article matches analysis #{payload['analysis_id']}; a duplicate database row was not created.",
            kind="warning",
        )

    metric_strip(
        (
            ("Article words", f"{payload['original_word_count']:,}", "Validated source text"),
            ("Reading time", f"{payload['reading_time_minutes']} min", "Estimated at normal pace"),
            ("Summary words", f"{payload['summary_word_count']:,}", payload["summary_length"]),
            ("Compression", f"{payload['compression_ratio_pct']:.1f}%", "Word-count reduction"),
            (
                "Calibrated confidence",
                f"{float(payload['calibrated_confidence']):.1%}",
                payload["confidence_band"],
            ),
            ("Total latency", f"{payload['processing_time']:.2f}s", "Local end-to-end runtime"),
        )
    )

    verdict_col, summary_col = st.columns([.88, 1.22], gap="large")
    with verdict_col:
        result_status(
            payload["prediction_label"],
            confidence=float(payload.get("confidence", max(
                payload["reliable_probability"], payload["misleading_probability"]
            ))),
            interpretation=verdict_interpretation(
                payload["prediction_label"],
                payload["confidence_band"],
                str(payload.get("review_reason", "")),
            ),
        )
        st.plotly_chart(
            confidence_gauge(
                float(payload["misleading_probability"]),
                float(payload["editorial_review_threshold"]),
            ),
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )
        callout(
            "Calibration and review policy",
            f"{payload['calibration_method']} calibration · validation-selected review threshold "
            f"{float(payload['editorial_review_threshold']):.0%}. Calibration measures reliability "
            "against benchmark labels, not factual verification.",
            kind="warning" if bool(payload.get("review_required")) else "neutral",
        )
    with summary_col:
        reading_panel(
            str(payload["article_title"]),
            str(payload["generated_summary"]),
            meta=(
                f"{payload['summary_method']} · {payload['summary_length']} · "
                f"{payload['summarization_time']:.3f}s"
            ),
        )

    section_heading(
        "03 · Article Information",
        "Source, extraction and linguistic context",
        "These fields describe the processed input. They are not independent evidence for or against the article.",
    )
    metadata_grid(
        (
            ("Input method", payload["input_type"]),
            ("Source domain", payload["source_domain"] or "Not available"),
            ("Source URL", payload["source_url"] or "Not available"),
            ("Author", payload["author"]),
            ("Publication date", payload["publication_date"]),
            ("Extraction method", payload["extractor"]),
            ("Language hint", payload["language_hint"]),
            ("Vocabulary coverage", f"{float(payload['vocabulary_coverage']):.1%}"),
            ("Out-of-vocabulary rate", f"{float(payload['oov_rate']):.1%}"),
            (
                "Supported-scope heuristic",
                "Review required" if bool(payload.get("domain_mismatch")) else "Within reference",
            ),
            ("Sentence count", payload.get("sentence_count", "Not available")),
            ("Average sentence length", f"{payload.get('average_sentence_words', 0):.1f} words"),
            ("Analysis date", payload["timestamp"]),
        )
    )

    section_heading(
        "04 · Model Explanation",
        "Why the linear model leaned this way",
        "The chart and term lists expose local TF-IDF × coefficient contributions from words "
        "present in this article. They are learned correlations, not factual evidence.",
    )
    st.plotly_chart(
        feature_contribution_chart(payload["explanation"]),
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )
    evidence_left, evidence_right = st.columns(2, gap="large")
    with evidence_left:
        evidence_terms(
            "Observed signals toward misleading",
            payload["explanation"].get("supports_misleading", []),
            direction="misleading",
        )
    with evidence_right:
        evidence_terms(
            "Observed signals toward reliable",
            payload["explanation"].get("supports_reliable", []),
            direction="reliable",
        )

    callout("Important disclaimer", DISCLAIMER, kind="warning")

    section_heading(
        "05 · Export",
        "Keep a portable copy of this analysis",
        "Exports are generated in memory. The original uploaded file or full source article is not retained.",
    )
    export_one, export_two, _ = st.columns([1, 1, 2])
    export_one.download_button(
        "Download Analysis JSON",
        analysis_json_bytes(payload),
        file_name=f"newslens_analysis_{payload['analysis_id']}.json",
        mime="application/json",
        use_container_width=True,
    )
    try:
        export_two.download_button(
            "Download Analysis PDF",
            analysis_pdf_bytes(payload),
            file_name=f"newslens_analysis_{payload['analysis_id']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except RuntimeError:
        export_two.info("Install reportlab to enable PDF export.")

footer("NewsLens AI · Primary Analysis Desk", "Independent summary and classification paths")
