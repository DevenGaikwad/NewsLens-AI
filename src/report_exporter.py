"""JSON and compact PDF exports for a completed analysis."""

from __future__ import annotations

import json
from html import escape
from io import BytesIO
from typing import Any

import pandas as pd

from .config import COPYRIGHT_NOTICE, DISCLAIMER, PROJECT_AUTHOR


SPREADSHEET_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def spreadsheet_safe_text(value: object) -> object:
    """Neutralise spreadsheet formulas while preserving readable exported text."""

    if isinstance(value, str) and value.startswith(SPREADSHEET_FORMULA_PREFIXES):
        return "'" + value
    return value


def archive_csv_bytes(frame: pd.DataFrame) -> bytes:
    """Return a UTF-8 CSV whose text cells cannot execute as spreadsheet formulas."""

    safe = frame.copy()
    for column in safe.columns:
        safe[column] = safe[column].map(spreadsheet_safe_text)
    return safe.to_csv(index=False).encode("utf-8")


def _paragraph_text(value: object) -> str:
    """Escape all ReportLab Paragraph markup in user-controlled values."""

    return escape(str(value if value is not None else ""), quote=True)


def analysis_json_bytes(payload: dict[str, Any]) -> bytes:
    """Return a readable JSON export."""

    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def analysis_pdf_bytes(payload: dict[str, Any]) -> bytes:
    """Return a simple, printable analysis report as PDF bytes."""

    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
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
        subject="Linguistic credibility-risk analysis; not a verified fact-check",
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
    story = [Paragraph("NewsLens AI - Article Intelligence Report", styles["NewsLensTitle"])]
    story.append(Paragraph(_paragraph_text(payload.get("article_title", "Untitled article")), styles["Heading2"]))
    table_data = [
        ["Input type", str(payload.get("input_type", ""))],
        ["Source", str(payload.get("source_domain", "Not available"))],
        ["Original words", str(payload.get("original_word_count", ""))],
        ["Summary method", str(payload.get("summary_method", ""))],
        ["Editorial risk outcome", str(payload.get("prediction_label", ""))],
        ["Calibrated reliable-label probability", f"{float(payload.get('reliable_probability', 0)):.1%}"],
        ["Calibrated misleading-label probability", f"{float(payload.get('misleading_probability', 0)):.1%}"],
        ["Calibrated confidence", f"{float(payload.get('calibrated_confidence', payload.get('confidence', 0))):.1%}"],
        ["Confidence band", str(payload.get("confidence_band", ""))],
        ["Calibration method", str(payload.get("calibration_method", ""))],
        ["Editorial-review status", str(payload.get("review_status", "Pending review"))],
        ["Model artifact ID", str(payload.get("model_version", ""))],
    ]
    table = Table(table_data, colWidths=[48 * mm, 108 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAE4D8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1A1917")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D4CEC2")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([table, Spacer(1, 10), Paragraph("Generated Summary", styles["Heading2"])])
    story.append(Paragraph(_paragraph_text(payload.get("generated_summary", "")), styles["BodyText"]))
    story.extend([Spacer(1, 10), Paragraph("Responsible-use notice", styles["Heading3"])])
    story.append(Paragraph(_paragraph_text(DISCLAIMER), styles["BodyText"]))
    story.extend([Spacer(1, 10), Paragraph(_paragraph_text(f"NewsLens AI · Designed and developed by {PROJECT_AUTHOR}"), styles["BodyText"])])
    story.append(Paragraph(_paragraph_text(COPYRIGHT_NOTICE), styles["BodyText"]))
    document.build(story)
    return stream.getvalue()
