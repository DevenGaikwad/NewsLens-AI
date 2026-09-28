"""A visible disagreement or ambiguous reference pair must not get a false automatic agreement."""

import pytest

from scripts.phase5w_challenge import build_cases
from src.config import REVIEW_REQUIRED_OUTCOME
from src.fake_news_predictor import load_model, predict_credibility
from src.model_diagnostics import assess_input


@pytest.fixture(scope="module")
def model():
    return load_model()


@pytest.mark.parametrize("index", [1, 3, 11, 13])
def test_single_visible_disagreement_never_auto_agrees(model, index: int) -> None:
    text = build_cases()[index]["text"]
    diagnostics = assess_input(text, model)
    result = predict_credibility(text, model, diagnostics=diagnostics)
    assert not diagnostics.domain_mismatch
    assert result.predicted_class == "reliable"  # Frozen model's known limitation.
    assert result.display_label == REVIEW_REQUIRED_OUTCOME
    assert result.review_required and result.score_withheld
    assert "visible field difference" in result.review_reason


@pytest.mark.parametrize("index", [6, 7, 8, 9])
def test_incomplete_ambiguous_or_ordinary_inputs_withhold_scores(model, index: int) -> None:
    text = build_cases()[index]["text"]
    diagnostics = assess_input(text, model)
    result = predict_credibility(text, model, diagnostics=diagnostics)
    assert diagnostics.domain_mismatch
    assert result.display_label == REVIEW_REQUIRED_OUTCOME
    assert result.review_required and result.score_withheld


def test_complete_packaged_conflict_still_uses_model_bound_score(model) -> None:
    from pathlib import Path

    text = (Path(__file__).resolve().parents[1] / "data/sample/misleading_style_article.txt").read_text()
    diagnostics = assess_input(text, model)
    result = predict_credibility(text, model, diagnostics=diagnostics)
    assert not diagnostics.domain_mismatch
    assert result.predicted_class == "misleading"
    assert not result.review_required and not result.score_withheld
    assert result.calibration_status == "verified"
