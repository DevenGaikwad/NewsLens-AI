"""Download/export bytes must be parseable and non-empty."""

import json
from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader

from src.config import HIGHER_RISK_OUTCOME, LOWER_RISK_OUTCOME
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
    exported = json.loads(analysis_json_bytes(_payload()))
    assert exported["article_title"] == "Export test"
    assert exported["supported_scope"] is True
    assert exported["score_reporting_status"] == "reported"


def test_pdf_export_opens() -> None:
    data = analysis_pdf_bytes(_payload())
    assert data.startswith(b"%PDF")
    assert len(PdfReader(BytesIO(data)).pages) >= 1


def test_pdf_uses_plain_reference_outcomes_and_keeps_json_labels() -> None:
    for machine_label, readable_label in (
        (LOWER_RISK_OUTCOME, "The article fields agree with the supplied reference"),
        (HIGHER_RISK_OUTCOME, "The article fields conflict with the supplied reference"),
    ):
        payload = _payload()
        payload["prediction_label"] = machine_label
        assert readable_label in _pdf_text(analysis_pdf_bytes(payload))
        assert json.loads(analysis_json_bytes(payload))["prediction_label"] == machine_label


def _pdf_text(data: bytes) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(data)).pages)


def test_pdf_probability_labels_values_and_columns_are_separate() -> None:
    data = analysis_pdf_bytes(_payload())
    reader = PdfReader(BytesIO(data))
    text = " ".join(_pdf_text(data).split())
    agree_label = "Fields agree - calibrated probability"
    conflict_label = "Fields conflict - calibrated probability"
    assert agree_label in text
    assert conflict_label in text
    assert text.index(agree_label) < text.index("51.0%") < text.index(conflict_label)
    assert text.index(conflict_label) < text.index("49.0%")
    assert f"{agree_label}51.0%" not in text
    assert f"{conflict_label}49.0%" not in text

    runs: list[tuple[str, float, float, float]] = []

    def collect(text_fragment, current_matrix, text_matrix, _font, font_size):
        stripped = text_fragment.strip()
        if stripped:
            runs.append(
                (
                    stripped,
                    float(current_matrix[4] + text_matrix[4]),
                    float(current_matrix[5] + text_matrix[5]),
                    float(font_size),
                )
            )

    reader.pages[0].extract_text(visitor_text=collect)
    split_x = 18 * mm + (A4[0] - 36 * mm) * 0.43
    label_runs = [run for run in runs if run[0] in {agree_label, conflict_label}]
    assert len(label_runs) == 2
    assert all(
        x + stringWidth(text_fragment, "Helvetica", size) <= split_x
        for text_fragment, x, _, size in label_runs
    )
    expected_values = {agree_label: "51.0%", conflict_label: "49.0%"}
    for label, _, label_y, _ in label_runs:
        matching_values = [
            run
            for run in runs
            if run[0] == expected_values[label] and abs(run[2] - label_y) < 0.1
        ]
        assert len(matching_values) == 1
        assert matching_values[0][1] >= split_x


def test_pdf_long_content_wraps_without_blank_pages_or_lost_footer() -> None:
    payload = _payload()
    payload["article_title"] = "A very long article title " * 18
    payload["source_domain"] = "https://example.test/" + "long-path-segment/" * 24
    payload["generated_summary"] = (
        "This deliberately long summary exercises automatic page wrapping and clean page breaks. "
        * 90
    )
    data = analysis_pdf_bytes(payload)
    reader = PdfReader(BytesIO(data))
    extracted_pages = [page.extract_text() or "" for page in reader.pages]
    assert len(extracted_pages) >= 2
    assert all(page.strip() for page in extracted_pages)
    assert "NewsLens AI · Designed and developed by Deven Gaikwad" in extracted_pages[-1]
    assert "© 2026 · All rights reserved" in extracted_pages[-1]
    assert extracted_pages[-1].count("Deven Gaikwad") == 1


def test_pdf_displayed_probabilities_preserve_runtime_rounding() -> None:
    payload = _payload()
    payload["reliable_probability"] = 0.0004
    payload["misleading_probability"] = 0.9996
    payload["source_domain"] = None
    text = " ".join(_pdf_text(analysis_pdf_bytes(payload)).split())
    assert "0.0%" in text
    assert "100.0%" in text
    assert "Not available" in text
    assert payload["reliable_probability"] + payload["misleading_probability"] == 1.0


def test_out_of_scope_pdf_withholds_directional_scores_but_json_stays_compatible() -> None:
    payload = _payload()
    payload.update(
        {
            "domain_mismatch": 1,
            "supported_scope": False,
            "reliable_probability": 0.116,
            "misleading_probability": 0.884,
            "calibrated_confidence": 0.884,
        }
    )
    pdf_text = " ".join(_pdf_text(analysis_pdf_bytes(payload)).split())
    assert "Outside supported comparison scope" in pdf_text
    assert "Not reported - outside supported scope" in pdf_text
    assert "11.6%" not in pdf_text
    assert "88.4%" not in pdf_text

    exported = json.loads(analysis_json_bytes(payload))
    assert exported["reliable_probability"] == 0.116
    assert exported["misleading_probability"] == 0.884
    assert exported["supported_scope"] is False
    assert exported["score_reporting_status"] == "withheld_outside_supported_scope"


def test_pdf_export_escapes_reportlab_markup() -> None:
    payload = _payload()
    payload["article_title"] = "<b>Not markup</b> & <img src='https://example.test/pixel'>"
    payload["generated_summary"] = "<a href='file:///etc/passwd'>literal link</a>"
    data = analysis_pdf_bytes(payload)
    text = _pdf_text(data)
    assert "Not markup" in text
    assert "literal link" in text
    assert "Designed and developed by Deven Gaikwad" in text


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


def test_archive_csv_withholds_out_of_scope_scores() -> None:
    frame = pd.DataFrame(
        [
            {
                "article_title": "Supported",
                "domain_mismatch": 0,
                "reliable_probability": 0.8,
                "misleading_probability": 0.2,
                "calibrated_confidence": 0.8,
                "predicted_class": "reliable",
            },
            {
                "article_title": "Ordinary external article",
                "domain_mismatch": 1,
                "reliable_probability": 0.12,
                "misleading_probability": 0.88,
                "calibrated_confidence": 0.88,
                "predicted_class": "misleading",
            },
        ]
    )
    rows = list(pd.read_csv(BytesIO(archive_csv_bytes(frame))).to_dict("records"))
    assert rows[0]["score_reporting_status"] == "reported"
    assert rows[0]["calibrated_confidence"] == 0.8
    assert rows[1]["score_reporting_status"] == "withheld_outside_supported_scope"
    assert pd.isna(rows[1]["reliable_probability"])
    assert pd.isna(rows[1]["misleading_probability"])
    assert pd.isna(rows[1]["calibrated_confidence"])
    assert pd.isna(rows[1]["predicted_class"])
