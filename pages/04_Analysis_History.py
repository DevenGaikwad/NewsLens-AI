"""Searchable personal editorial archive backed by local SQLite."""

from __future__ import annotations

from datetime import date
import html

import pandas as pd
import streamlit as st

from src.config import REPORTS_DIR
from src.database import (
    clear_history,
    delete_analysis,
    get_analysis,
    list_analyses,
    update_editorial_review,
)
from src.editorial_review import REVIEW_STATUSES
from src.model_diagnostics import assess_drift, load_reference_profile
from src.newsroom_analytics import (
    activity_over_time,
    confidence_distribution,
    newsroom_summary,
    privacy_safe_analytics_export,
    review_distribution,
    risk_distribution,
)
from src.report_exporter import analysis_json_bytes, analysis_pdf_bytes, archive_csv_bytes
from src.session_history import session_history_path
from src.visualizations import (
    model_comparison_chart,
    newsroom_activity_chart,
    newsroom_distribution_chart,
)
from ui import (
    callout,
    configure_page,
    empty_state,
    footer,
    metadata_grid,
    metric_strip,
    page_header,
    reading_panel,
    result_status,
    section_heading,
)


def timestamp_label(value: object) -> str:
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime("%d %b %Y · %H:%M UTC")


configure_page("NewsLens AI | Editorial Archive", active="history")
history_database = session_history_path()
page_header(
    "Personal Editorial Archive",
    "Your analysis record,\nprivate to this session.",
    "Search, filter, sort, inspect, reopen, export, or explicitly delete structured analysis "
    "records. Uploaded files and full original article text are not stored.",
)

base_frame = list_analyses(limit=5000, path=history_database)
summary = newsroom_summary(base_frame)
section_heading(
    "01 · Newsroom Analytics",
    "Session-local editorial signals",
    "These aggregates describe only this visitor's isolated archive. Full articles, personal data, "
    "review notes, and source URLs are excluded from analytics and its export.",
)
metric_strip(
    (
        ("Analysed articles", f"{summary['analysed_articles']:,}", "Current visitor session"),
        ("Review required", f"{summary['editorial_review_rate']:.1%}", "Model or scope abstention"),
        ("Inconclusive", f"{summary['inconclusive_rate']:.1%}", "Human review status"),
        (
            "Average latency",
            f"{summary['average_inference_latency_seconds']:.2f}s",
            "End-to-end per analysis",
        ),
        ("Pending reviews", f"{summary.get('pending_reviews', 0):,}", "Human workflow queue"),
    )
)

if not base_frame.empty:
    analytics_left, analytics_right = st.columns(2, gap="large")
    with analytics_left:
        st.plotly_chart(
            newsroom_distribution_chart(risk_distribution(base_frame), category="Outcome"),
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )
        st.caption("Predicted-risk and abstention outcomes in the current private archive.")
    with analytics_right:
        st.plotly_chart(
            newsroom_distribution_chart(
                confidence_distribution(base_frame), category="Confidence band"
            ),
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )
        st.caption("Calibrated confidence bands; review outcomes are shown separately.")

    review_left, activity_right = st.columns(2, gap="large")
    with review_left:
        st.plotly_chart(
            newsroom_distribution_chart(
                review_distribution(base_frame), category="Review status"
            ),
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )
        st.caption("Human editorial-review statuses for session-local records.")
    with activity_right:
        activity = activity_over_time(base_frame)
        if not activity.empty:
            st.plotly_chart(
                newsroom_activity_chart(activity),
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )
        st.caption("Analysis activity over time where dated observations exist.")

    st.download_button(
        "Export Privacy-Safe Analytics as CSV",
        archive_csv_bytes(privacy_safe_analytics_export(base_frame)),
        file_name="newslens_newsroom_analytics.csv",
        mime="text/csv",
    )
    comparison_path = REPORTS_DIR / "model_benchmark_results.csv"
    if comparison_path.exists():
        with st.expander("Open controlled model comparison"):
            comparison = pd.read_csv(comparison_path)
            st.plotly_chart(
                model_comparison_chart(comparison),
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )
            st.dataframe(
                comparison[
                    [
                        "model",
                        "macro_f1",
                        "roc_auc",
                        "calibrated_brier_score",
                        "calibrated_ece",
                        "mean_inference_ms_per_article",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )

section_heading(
    "02 · Drift Readiness",
    "Distribution checks without automatic retraining",
    "Warnings compare aggregate session observations with benchmark reference ranges. A warning "
    "indicates distributional change, not automatic model failure.",
)
drift = assess_drift(
    base_frame,
    reference_profile=load_reference_profile(),
    total_attempts=int(st.session_state.get("analysis_attempts_total", len(base_frame))),
    invalid_attempts=int(st.session_state.get("analysis_attempts_invalid", 0)),
)
if drift["status"] == "insufficient":
    callout(
        "Drift status",
        str(drift["message"]),
        kind="warning",
    )
    st.caption(
        f"{drift['observations']} of {drift['minimum_observations']} required observations are available."
    )
else:
    callout(
        "Drift status",
        str(drift["message"]),
        kind="warning" if drift["status"] == "watch" else "success",
    )
    st.dataframe(pd.DataFrame(drift["indicators"]), hide_index=True, use_container_width=True)

if base_frame.empty:
    empty_state(
        "No archived analyses yet",
        "Run an article from the Analyse Article page. Its private session record will appear here.",
    )
    footer("NewsLens AI · Editorial Archive", "SQLite · session-isolated history")
    st.stop()

base_timestamps = pd.to_datetime(base_frame["timestamp"], utc=True, errors="coerce")
valid_dates = base_timestamps.dropna().dt.date
min_date = valid_dates.min() if not valid_dates.empty else date.today()
max_date = valid_dates.max() if not valid_dates.empty else date.today()

section_heading(
    "03 · Find Records",
    "Search and filter the archive",
    "Filters operate only on this visitor session's SQLite result set and do not send article history to an external service.",
)
search_col, label_col, sort_col = st.columns([1.5, 1, 1], gap="large")
search = search_col.text_input(
    "Search title, source, or summary",
    placeholder="Enter a word, domain, or phrase",
)
label = label_col.selectbox(
    "Risk outcome",
    [
        "All",
        "Lower misleading-content risk indicated",
        "Higher misleading-content risk indicated",
        "Editorial review required",
    ],
)
sort_order = sort_col.selectbox(
    "Sort order",
    ["Newest first", "Oldest first", "Highest risk", "Lowest risk"],
)
date_range = st.date_input(
    "Analysis date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

frame = list_analyses(search=search, label=label, limit=5000, path=history_database)
frame["_timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    frame = frame[
        frame["_timestamp"].dt.date.between(start_date, end_date, inclusive="both")
    ]

if sort_order == "Oldest first":
    frame = frame.sort_values("_timestamp", ascending=True)
elif sort_order == "Highest risk":
    frame = frame.sort_values("misleading_probability", ascending=False)
elif sort_order == "Lowest risk":
    frame = frame.sort_values("misleading_probability", ascending=True)
else:
    frame = frame.sort_values("_timestamp", ascending=False)

if frame.empty:
    empty_state("No matching records", "Adjust the search, verdict, or date filters.")
    footer("NewsLens AI · Editorial Archive", "No current filter matches")
    st.stop()

metric_strip(
    (
        ("Matching records", f"{len(frame):,}", "Current filter result"),
        (
            "Average risk",
            f"{frame['misleading_probability'].mean():.1%}",
            "Mean misleading probability",
        ),
        (
            "Latest record",
            timestamp_label(frame.iloc[0]["timestamp"]).split(" · ")[0],
            "After current sort",
        ),
        ("Storage", "Private SQLite", "Temporary on public cloud hosting"),
    )
)

export_frame = frame.drop(columns=["_timestamp"], errors="ignore")
st.download_button(
    "Export Filtered Archive as CSV",
    archive_csv_bytes(export_frame),
    file_name="newslens_editorial_archive.csv",
    mime="text/csv",
)

section_heading(
    "04 · Archive Index",
    "Compact editorial records",
    "The first 25 matching records are shown. Use the filters to narrow a larger archive.",
)
visible_frame = frame.head(25)
for _, row in visible_frame.iterrows():
    title = str(row.get("article_title") or "Untitled article")
    source = str(row.get("source_domain") or row.get("input_type") or "Local input")
    summary = str(row.get("generated_summary") or "")
    safe_title = html.escape(title)
    safe_source = html.escape(source)
    safe_summary = html.escape(summary)
    safe_label = html.escape(str(row["prediction_label"]))
    st.markdown(
        f"""
<article class="archive-row">
  <div class="archive-meta">#{int(row['analysis_id'])} · {timestamp_label(row['timestamp'])} · {safe_source} · {safe_label} · risk {float(row['misleading_probability']):.1%}</div>
  <h3>{safe_title}</h3>
  <div class="archive-preview">{safe_summary}</div>
</article>
""",
        unsafe_allow_html=True,
    )
    if st.button(
        f"Inspect Analysis #{int(row['analysis_id'])}",
        key=f"inspect_{int(row['analysis_id'])}",
    ):
        st.session_state["archive_selected_id"] = int(row["analysis_id"])
        st.rerun()

with st.expander("Open tabular archive view"):
    display_columns = [
        "analysis_id",
        "timestamp",
        "article_title",
        "source_domain",
        "prediction_label",
        "calibrated_confidence",
        "review_status",
        "summary_method",
        "original_word_count",
    ]
    st.dataframe(
        visible_frame[display_columns],
        hide_index=True,
        use_container_width=True,
        column_config={
            "calibrated_confidence": st.column_config.ProgressColumn(
                "Calibrated confidence", min_value=0.0, max_value=1.0, format="%.0f%%"
            )
        },
    )

available_ids = frame["analysis_id"].astype(int).tolist()
selected_id = int(st.session_state.get("archive_selected_id", available_ids[0]))
if selected_id not in available_ids:
    selected_id = available_ids[0]
    st.session_state["archive_selected_id"] = selected_id
record = get_analysis(selected_id, path=history_database)

if record:
    section_heading(
        "05 · Selected Record",
        str(record["article_title"]),
        f"Analysis #{selected_id} · {timestamp_label(record['timestamp'])}",
    )
    verdict_col, summary_col = st.columns([.82, 1.18], gap="large")
    with verdict_col:
        result_status(
            record["prediction_label"],
            confidence=float(record["calibrated_confidence"]),
            interpretation=(
                f"Archived {record['confidence_band'].lower()}-band risk signal from model "
                f"{record['model_version']}. {record.get('review_reason') or ''}"
            ),
        )
    with summary_col:
        reading_panel(
            str(record["article_title"]),
            str(record["generated_summary"]),
            meta=f"{record['summary_method']} · {record['summary_length']}",
        )

    metadata_grid(
        (
            ("Input type", record["input_type"]),
            ("Source domain", record["source_domain"] or "Not available"),
            ("Source URL", record["source_url"] or "Not available"),
            ("Calibrated reliable probability", f"{float(record['reliable_probability']):.1%}"),
            ("Calibrated misleading probability", f"{float(record['misleading_probability']):.1%}"),
            ("Calibrated confidence", f"{float(record['calibrated_confidence']):.1%}"),
            ("Review status", record["review_status"]),
            ("Vocabulary coverage", f"{float(record['vocabulary_coverage']):.1%}"),
            ("Out-of-vocabulary rate", f"{float(record['oov_rate']):.1%}"),
            ("Original words", f"{int(record['original_word_count']):,}"),
            ("Processing time", f"{float(record['processing_time']):.2f}s"),
            ("Analysis date", timestamp_label(record["timestamp"])),
        )
    )

    section_heading(
        "06 · Human Editorial Review",
        "Record evidence and a final assessment",
        "This academic prototype stores the review only in the current visitor's session-scoped "
        "SQLite file. Supporting URLs are references for a human editor; the application does not "
        "treat them as automatic proof.",
    )
    if bool(record.get("review_required")):
        callout(
            "Queue reason",
            str(record.get("review_reason") or "The model or input-quality policy requires review."),
            kind="warning",
        )
    status_value = str(record.get("review_status") or "Pending review")
    status_index = REVIEW_STATUSES.index(status_value) if status_value in REVIEW_STATUSES else 0
    with st.form(f"editorial_review_{selected_id}"):
        review_status = st.selectbox(
            "Review status",
            REVIEW_STATUSES,
            index=status_index,
        )
        reviewer_notes = st.text_area(
            "Reviewer notes",
            value=str(record.get("reviewer_notes") or ""),
            height=140,
            help="Record reasoning, evidence gaps, and checks performed. Do not enter private personal data.",
        )
        supporting_urls = st.text_area(
            "Supporting-source URLs (one public HTTP(S) URL per line)",
            value=str(record.get("supporting_source_urls") or ""),
            height=110,
        )
        final_assessment = st.text_area(
            "Final editorial assessment",
            value=str(record.get("final_editorial_assessment") or ""),
            height=120,
            help="Summarise the human conclusion and any remaining uncertainty.",
        )
        save_review = st.form_submit_button("Save Editorial Review", type="primary")
    if save_review:
        try:
            if update_editorial_review(
                selected_id,
                review_status=review_status,
                reviewer_notes=reviewer_notes,
                supporting_source_urls=supporting_urls,
                final_editorial_assessment=final_assessment,
                path=history_database,
            ):
                st.success("Editorial review saved in this visitor's private session archive.")
                st.rerun()
        except ValueError as exc:
            st.error(str(exc))

    export_one, export_two, _ = st.columns([1, 1, 2])
    export_one.download_button(
        "Download Selected JSON",
        analysis_json_bytes(record),
        file_name=f"newslens_analysis_{selected_id}.json",
        mime="application/json",
        use_container_width=True,
    )
    try:
        export_two.download_button(
            "Download Selected PDF",
            analysis_pdf_bytes(record),
            file_name=f"newslens_analysis_{selected_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except RuntimeError:
        export_two.info("Install reportlab to enable PDF export.")

section_heading(
    "07 · Record Control",
    "Confirmed deletion only",
    "Deletion affects the local SQLite archive and cannot be undone from inside the application.",
)
with st.expander("Delete archive records"):
    confirm_one = st.checkbox(f"Confirm deletion of analysis #{selected_id}")
    if st.button("Delete Selected Analysis", disabled=not confirm_one):
        if delete_analysis(selected_id, path=history_database):
            st.session_state.pop("archive_selected_id", None)
            st.success("The selected analysis was deleted.")
            st.rerun()
    st.markdown("#### Clear the complete archive")
    confirm_phrase = st.text_input("Type CLEAR ALL to confirm")
    if st.button("Clear Complete Archive", disabled=confirm_phrase != "CLEAR ALL"):
        removed = clear_history(path=history_database)
        st.session_state.pop("archive_selected_id", None)
        st.success(f"Removed {removed} history records.")
        st.rerun()

callout(
    "Privacy boundary",
    "The archive stores analysis fields, probabilities, summary, metadata, and a duplicate-detection "
    "hash in a session-isolated SQLite file. It does not retain uploaded files or expose one "
    "visitor's records to another visitor.",
    kind="success",
)
footer("NewsLens AI · Editorial Archive", "SQLite · searchable session history")
