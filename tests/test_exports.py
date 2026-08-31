"""Download/export bytes must be parseable and non-empty."""

import json
from io import BytesIO

import pandas as pd
from pypdf import PdfReader

from src.report_exporter import analysis_json_bytes, analysis_pdf_bytes, archive_csv_bytes


def _payload() -> dict[str, object]:
    return {
        "article_title": "Export test",
        "input_type": "Direct text",
        "source_domain": "example.test",
        "original_word_count": 100,
        "summary_method": "Extractive",
        "generated_summary": "A short summary generated for an automated export test.",
        "prediction_label": "Editorial review required",
        "reliable_probability": 0.51,
        "misleading_probability": 0.49,
        "calibrated_confidence": 0.51,
        "confidence_band": "Review",
        "calibration_method": "Platt scaling",
        "review_status": "Pending review",
        "model_version": "test-v1",
    }


def test_json_export_round_trip() -> None:
    assert json.loads(analysis_json_bytes(_payload()))["article_title"] == "Export test"


def test_pdf_export_opens() -> None:
    data = analysis_pdf_bytes(_payload())
    assert data.startswith(b"%PDF")
    assert len(PdfReader(BytesIO(data)).pages) >= 1


def test_pdf_export_escapes_reportlab_markup() -> None:
    payload = _payload()
    payload["article_title"] = "<b>Not markup</b> & <img src='https://example.test/pixel'>"
    payload["generated_summary"] = "<a href='file:///etc/passwd'>literal link</a>"
    data = analysis_pdf_bytes(payload)
    text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(data)).pages)
    assert "Not markup" in text
    assert "literal link" in text
    assert "Deven Sachin Gaikwad" in text


def test_archive_csv_neutralises_formula_injection() -> None:
    frame = pd.DataFrame(
        [
            {
                "article_title": "=HYPERLINK(\"https://example.test\",\"open\")",
                "source_domain": "+cmd|' /C calc'!A0",
                "generated_summary": "@SUM(1+1)",
                "safe_number": 42,
            },
            {
                "article_title": "\tmalicious",
                "source_domain": "\rmalicious",
                "generated_summary": "-1+2",
                "safe_number": 7,
            },
        ]
    )
    csv_text = archive_csv_bytes(frame).decode("utf-8")
    assert "'=HYPERLINK" in csv_text
    assert "'+cmd" in csv_text
    assert "'@SUM" in csv_text
    assert "'\tmalicious" in csv_text
    assert "'\rmalicious" in csv_text
    assert "'-1+2" in csv_text
