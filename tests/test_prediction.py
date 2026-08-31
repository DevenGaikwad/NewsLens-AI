"""Tests for saved-model loading, probabilities, labels, and local XAI."""

from pathlib import Path

import pytest

from src.fake_news_predictor import ModelLoadError, load_model, predict_credibility
from src.model_diagnostics import assess_input


def test_packaged_model_loads_without_retraining(sample_article: str) -> None:
    model = load_model()
    result = predict_credibility(sample_article, model)
    assert result.predicted_class in {"reliable", "misleading"}
    assert result.display_label in {
        "Lower misleading-content risk indicated",
        "Higher misleading-content risk indicated",
        "Editorial review required",
    }
    assert abs(result.reliable_probability + result.misleading_probability - 1.0) <= 0.001
    assert 0.0 <= result.confidence <= 1.0
    assert result.calibration_status == "verified"
    assert result.calibration_method == "Platt scaling"
    assert result.editorial_review_threshold == 0.59
    assert set(result.explanation) == {"supports_misleading", "supports_reliable"}


def test_validation_selected_threshold_can_require_editorial_review() -> None:
    model = load_model()
    text = (Path(__file__).resolve().parents[1] / "data/sample/uncertain_style_article.txt").read_text(
        encoding="utf-8"
    )
    result = predict_credibility(text, model, diagnostics=assess_input(text, model))
    assert result.display_label == "Editorial review required"
    assert result.review_required is True
    assert "review threshold" in result.review_reason


def test_missing_model_has_actionable_error(tmp_path: Path) -> None:
    with pytest.raises(ModelLoadError, match="training/train_fake_news_models.py"):
        load_model(tmp_path / "missing.joblib")
