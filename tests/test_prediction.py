"""Tests for the public synthetic model, calibration, labels, and abstention."""

from pathlib import Path

import pytest

from src.config import HIGHER_RISK_OUTCOME, LOWER_RISK_OUTCOME, REVIEW_REQUIRED_OUTCOME
from src.fake_news_predictor import ModelLoadError, load_model, predict_credibility
from src.model_diagnostics import assess_input


ROOT = Path(__file__).resolve().parents[1]


def _sample(name: str) -> str:
    return (ROOT / "data" / "sample" / name).read_text(encoding="utf-8")


def test_packaged_model_loads_and_is_calibration_bound() -> None:
    model = load_model()
    result = predict_credibility(_sample("reliable_style_article.txt"), model)
    assert result.predicted_class == "reliable"
    assert result.display_label == LOWER_RISK_OUTCOME
    assert result.calibration_status == "verified"
    assert result.calibration_method == "Platt scaling"
    assert result.editorial_review_threshold == 0.5
    assert result.review_required is False
    assert abs(result.reliable_probability + result.misleading_probability - 1.0) <= 0.001


def test_visible_mismatches_produce_contradicting_outcome() -> None:
    model = load_model()
    text = _sample("misleading_style_article.txt")
    result = predict_credibility(text, model, diagnostics=assess_input(text, model))
    assert result.predicted_class == "misleading"
    assert result.display_label == HIGHER_RISK_OUTCOME
    assert result.review_required is False


def test_missing_fact_blocks_force_editorial_review() -> None:
    model = load_model()
    text = _sample("uncertain_style_article.txt")
    result = predict_credibility(text, model, diagnostics=assess_input(text, model))
    assert result.display_label == REVIEW_REQUIRED_OUTCOME
    assert result.review_required is True
    assert "Reference note" in result.review_reason


def test_missing_model_has_actionable_error(tmp_path: Path) -> None:
    with pytest.raises(ModelLoadError, match="training/train_synthetic_model.py"):
        load_model(tmp_path / "missing.joblib")
