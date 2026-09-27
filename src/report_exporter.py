"""JSON and compact PDF exports for a completed analysis."""

from __future__ import annotations

import json
from html import escape
from io import BytesIO
from typing import Any

import pandas as pd

from .config import (
    CALIBRATED_CONFIDENCE_EXPLANATION,
    CALIBRATED_SCORE_EXPLANATION,
    DISCLAIMER,
    EDITORIAL_REVIEW_EXPLANATION,
    FIELDS_AGREE_PROBABILITY_LABEL,
    FIELDS_CONFLICT_PROBABILITY_LABEL,
    HIGHER_RISK_OUTCOME,
    LOWER_RISK_OUTCOME,
    OUT_OF_SCOPE_EXPLANATION,
    PUBLIC_AUTHOR,
    PUBLIC_COPYRIGHT_NOTICE,
    PROJECT_AUTHOR,
    REFERENCE_AGREEMENT_OUTCOME,
    REFERENCE_COMPARISON_CONFIDENCE_LABEL,
    REFERENCE_CONFLICT_OUTCOME,
)


SPREADSHEET_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def spreadsheet_safe_text(value: object) -> object:
    """Neutralise spreadsheet formulas while preserving readable exported text."""

    if isinstance(value, str) and value.startswith(SPREADSHEET_FORMULA_PREFIXES):
        return "'" + value
    return value


def archive_csv_bytes(frame: pd.DataFrame) -> bytes:
    """Return a UTF-8 CSV whose text cells cannot execute as spreadsheet formulas."""

    safe = frame.copy()
    if "domain_mismatch" in safe.columns:
        outside_scope = pd.to_numeric(
            safe["domain_mismatch"], errors="coerce"
        ).fillna(0).astype(bool)
        if "score_reporting_status" not in safe.columns:
            safe.insert(
                0,
                "score_reporting_status",
                outside_scope.map(
                    lambda value: (
                        "withheld_outside_supported_scope" if value else "reported"
                    )
                ),
            )
        score_columns = [
            column
            for column in (
                "reliable_probability",
                "misleading_probability",
                "calibrated_confidence",
            )
            if column in safe.columns
        ]
        if score_columns:
            safe.loc[outside_scope, score_columns] = pd.NA
    for column in safe.columns:
        safe[column] = safe[column].map(spreadsheet_safe_text)
    return safe.to_csv(index=False).encode("utf-8")


def _paragraph_text(value: object) -> str:
    """Escape all ReportLab Paragraph markup in user-controlled values."""

    return escape(str(value if value is not None else ""), quote=True)


def analysis_json_bytes(payload: dict[str, Any]) -> bytes:
    """Return a readable JSON export."""

    export_payload = dict(payload)
    scope_supported = bool(
        export_payload.get(
            "supported_scope", not bool(export_payload.get("domain_mismatch", False))
        )
    )
    export_payload.setdefault("supported_scope", scope_supported)
    export_payload.setdefault(
        "score_reporting_status",
        "reported" if scope_supported else "withheld_outside_supported_scope",
    )
    return json.dumps(export_payload, indent=2, ensure_ascii=False).encode("utf-8")


def analysis_pdf_bytes(payload: dict[str, Any]) -> bytes:
    """Return a simple, printable analysis report as PDF bytes."""

    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError("PDF export needs the reportlab package.") from exc

    stream = BytesIO()
    document = SimpleDocTemplate(
        stream,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="NewsLens AI Analysis",
        author=PROJECT_AUTHOR,
        creator="NewsLens AI",
        subject="Synthetic ledger-consistency analysis; not a verified fact-check",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="NewsLensTitle",
            parent=styles["Title"],
            textColor=colors.HexColor("#40352C"),
            alignment=TA_CENTER,
            fontSize=21,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NewsLensTableLabel",
            parent=styles["BodyText"],
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            splitLongWords=True,
            textColor=colors.HexColor("#1A1917"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NewsLensTableValue",
            parent=styles["BodyText"],
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            splitLongWords=True,
            textColor=colors.HexColor("#1A1917"),
        )
    )
    story = [Paragraph("NewsLens AI - Article Intelligence Report", styles["NewsLensTitle"])]
    story.append(
        Paragraph(
            _paragraph_text(payload.get("article_title") or "Untitled article"),
            styles["Heading2"],
        )
    )
    scope_supported = bool(
        payload.get("supported_scope", not bool(payload.get("domain_mismatch", False)))
    )
    display_labels = {
        LOWER_RISK_OUTCOME: REFERENCE_AGREEMENT_OUTCOME,
        HIGHER_RISK_OUTCOME: REFERENCE_CONFLICT_OUTCOME,
    }
    prediction_label = str(payload.get("prediction_label", ""))
    displayed_outcome = (
        display_labels.get(prediction_label, prediction_label)
        if scope_supported
        else "Outside supported comparison scope"
    )
    score_rows = (
        [
            [FIELDS_AGREE_PROBABILITY_LABEL, f"{float(payload.get('reliable_probability', 0)):.1%}"],
            [FIELDS_CONFLICT_PROBABILITY_LABEL, f"{float(payload.get('misleading_probability', 0)):.1%}"],
            [REFERENCE_COMPARISON_CONFIDENCE_LABEL, f"{float(payload.get('calibrated_confidence', payload.get('confidence', 0))):.1%}"],
            ["Confidence band", str(payload.get("confidence_band", ""))],
        ]
        if scope_supported
        else [
            [FIELDS_AGREE_PROBABILITY_LABEL, "Not reported - outside supported scope"],
            [FIELDS_CONFLICT_PROBABILITY_LABEL, "Not reported - outside supported scope"],
            [REFERENCE_COMPARISON_CONFIDENCE_LABEL, "Not reported - outside supported scope"],
            ["Confidence band", "Outside supported scope"],
        ]
    )
    table_values = [
        ["Input type", str(payload.get("input_type", ""))],
        ["Source", str(payload.get("source_domain") or "Not available")],
        ["Original words", str(payload.get("original_word_count", ""))],
        ["Summary method", str(payload.get("summary_method", ""))],
        ["Reference comparison outcome", displayed_outcome],
        ["Supported comparison scope", "Yes" if scope_supported else "No"],
        *score_rows,
        ["Calibration method", str(payload.get("calibration_method", ""))],
        ["Editorial-review status", str(payload.get("review_status", "Pending review"))],
        ["Model artifact ID", str(payload.get("model_version", ""))],
    ]
    table_data = [
        [
            Paragraph(_paragraph_text(label), styles["NewsLensTableLabel"]),
            Paragraph(_paragraph_text(value), styles["NewsLensTableValue"]),
        ]
        for label, value in table_values
    ]
    usable_width = A4[0] - document.leftMargin - document.rightMargin
    label_width = usable_width * 0.43
    value_width = usable_width - label_width
    table = Table(
        table_data,
        colWidths=[label_width, value_width],
        hAlign="LEFT",
        splitByRow=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAE4D8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1A1917")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D4CEC2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 10),
            Paragraph("What do these scores mean?", styles["Heading3"]),
            Paragraph(
                _paragraph_text(
                    CALIBRATED_SCORE_EXPLANATION if scope_supported else OUT_OF_SCOPE_EXPLANATION
                ),
                styles["BodyText"],
            ),
            Spacer(1, 4),
            Paragraph(
                _paragraph_text(
                    CALIBRATED_CONFIDENCE_EXPLANATION
                    if scope_supported
                    else "The raw machine-readable JSON fields remain available for compatibility, "
                    "but they must not be interpreted as factual credibility."
                ),
                styles["BodyText"],
            ),
            Spacer(1, 4),
            Paragraph(
                _paragraph_text(
                    EDITORIAL_REVIEW_EXPLANATION
                    if scope_supported
                    else "The input remains available for human editorial review without an "
                    "automatic directional claim."
                ),
                styles["BodyText"],
            ),
            Spacer(1, 10),
            Paragraph("Generated Summary", styles["Heading2"]),
        ]
    )
    story.append(Paragraph(_paragraph_text(payload.get("generated_summary", "")), styles["BodyText"]))
    story.extend([Spacer(1, 10), Paragraph("Responsible-use notice", styles["Heading3"])])
    story.append(Paragraph(_paragraph_text(DISCLAIMER), styles["BodyText"]))
    story.extend(
        [
            Spacer(1, 10),
            Paragraph(
                _paragraph_text(f"NewsLens AI · Designed and developed by {PUBLIC_AUTHOR}"),
                styles["BodyText"],
            ),
        ]
    )
    story.append(Paragraph(_paragraph_text(PUBLIC_COPYRIGHT_NOTICE), styles["BodyText"]))
    document.build(story)
    return stream.getvalue()
