"""Contracts for benchmarking, calibration, review, analytics, and drift readiness."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.calibration import load_calibration
from src.editorial_review import REVIEW_STATUSES, normalise_supporting_urls
from src.fake_news_predictor import load_model
from src.model_diagnostics import INSUFFICIENT_DRIFT_MESSAGE, assess_drift, assess_input
from src.newsroom_analytics import privacy_safe_analytics_export


ROOT = Path(__file__).resolve().parents[1]


def _json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_controlled_benchmark_has_three_candidates_and_no_partition_leakage() -> None:
    summary = _json("reports/model_benchmark_summary.json")
    assert [item["model"] for item in summary["models"]] == [
        "Logistic Regression",
        "Linear SVC",
        "Multinomial Naive Bayes",
    ]
    assert summary["partitions"]["train_rows"] == 19_200
    assert summary["partitions"]["validation_rows"] == 2_399
    assert summary["partitions"]["test_rows"] == 2_399
    assert summary["leakage_audit"]["cross_partition_pairs_after_controls"] == 0
    assert summary["selection"]["selected_model"] == "Logistic Regression"
    assert summary["selection"]["packaged_model_unchanged"] is True


@pytest.mark.private_model
def test_calibration_improves_production_brier_and_ece() -> None:
    evidence = _json("reports/calibration_validation.json")["production_model"]
    assert evidence["calibrated_brier_score"] < evidence["uncalibrated_brier_score"]
    assert (
        evidence["calibrated_expected_calibration_error"]
        < evidence["uncalibrated_expected_calibration_error"]
    )
    calibration = load_calibration()
    assert calibration.method == "Platt scaling"
    assert calibration.editorial_review_threshold == 0.59


@pytest.mark.private_model
def test_input_diagnostics_expose_vocabulary_and_scope_signals(sample_article: str) -> None:
    model = load_model()
    result = assess_input(sample_article, model)
    assert 0.0 <= result.vocabulary_coverage <= 1.0
    assert result.out_of_vocabulary_rate == pytest.approx(1 - result.vocabulary_coverage, abs=1e-6)
    assert result.language_hint == "English/Latin script"


def test_drift_reports_insufficient_observations_before_minimum() -> None:
    result = assess_drift(pd.DataFrame())
    assert result["status"] == "insufficient"
    assert result["message"] == INSUFFICIENT_DRIFT_MESSAGE


def test_drift_uses_only_aggregate_analysis_fields() -> None:
    frame = pd.DataFrame(
        [
            {
                "original_word_count": 300 + index,
                "vocabulary_coverage": 0.72,
                "oov_rate": 0.28,
                "predicted_class": "reliable" if index % 2 else "misleading",
                "calibrated_confidence": 0.88,
                "language_mismatch": 0,
                "domain_mismatch": 0,
            }
            for index in range(20)
        ]
    )
    result = assess_drift(frame, total_attempts=22, invalid_attempts=2)
    names = {item["indicator"] for item in result["indicators"]}
    assert result["status"] in {"watch", "within_reference"}
    assert {
        "Median article length",
        "Mean vocabulary coverage",
        "Mean out-of-vocabulary rate",
        "Higher-risk prediction share",
        "Mean calibrated confidence",
        "Invalid-input rate",
        "Language-mismatch rate",
        "Domain-mismatch heuristic rate",
    } == names


def test_analytics_export_excludes_articles_notes_urls_and_identifiers() -> None:
    frame = pd.DataFrame(
        [
            {
                "analysis_id": 9,
                "article_title": "Private title",
                "generated_summary": "Private summary",
                "reviewer_notes": "Private notes",
                "supporting_source_urls": "https://example.test/private",
                "review_required": 1,
                "review_status": "Inconclusive",
                "processing_time": 0.4,
            }
        ]
    )
    export = privacy_safe_analytics_export(frame)
    text = export.to_csv(index=False)
    for private_value in ("Private title", "Private summary", "Private notes", "example.test", "analysis_id"):
        assert private_value not in text


def test_review_statuses_are_fixed_and_supporting_urls_fail_closed() -> None:
    assert REVIEW_STATUSES == (
        "Pending review",
        "Evidence supports the claim",
        "Evidence contradicts the claim",
        "Inconclusive",
        "Out of supported scope",
    )
    assert normalise_supporting_urls("https://example.test/evidence") == (
        "https://example.test/evidence",
    )
    with pytest.raises(ValueError, match="Private-network"):
        normalise_supporting_urls("http://127.0.0.1/private")
