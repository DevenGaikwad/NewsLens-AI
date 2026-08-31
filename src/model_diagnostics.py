"""Inference-time input diagnostics and lightweight drift readiness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import MIN_ARTICLE_WORDS, MIN_DRIFT_OBSERVATIONS, MODEL_REFERENCE_PROFILE_PATH
from .text_preprocessor import detect_language_hint, text_for_model
from .utils import load_json, word_count


INSUFFICIENT_DRIFT_MESSAGE = "Insufficient observations for a reliable drift assessment."


@dataclass(frozen=True)
class InputDiagnostics:
    word_count: int
    vocabulary_coverage: float
    out_of_vocabulary_rate: float
    language_hint: str
    language_mismatch: bool
    domain_mismatch: bool
    input_quality_inadequate: bool
    review_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["review_reasons"] = list(self.review_reasons)
        return payload


def load_reference_profile(path: Path | str = MODEL_REFERENCE_PROFILE_PATH) -> dict[str, Any]:
    payload = load_json(Path(path), {}) or {}
    return payload if isinstance(payload, dict) else {}


def _unigram_tokens(text: str) -> list[str]:
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text_for_model(text))


def assess_input(
    text: str,
    pipeline: Any,
    reference_profile: dict[str, Any] | None = None,
) -> InputDiagnostics:
    """Compare one input with the training vocabulary and aggregate reference ranges.

    The domain flag is a transparent heuristic, not a semantic domain classifier.
    """

    profile = reference_profile or load_reference_profile()
    tokens = _unigram_tokens(text)
    vocabulary = set(getattr(pipeline.named_steps.get("tfidf"), "vocabulary_", {}))
    known = sum(token in vocabulary for token in tokens) if vocabulary else 0
    coverage = known / len(tokens) if tokens else 0.0
    oov_rate = 1.0 - coverage if tokens else 1.0
    article_words = word_count(text)
    language_hint = detect_language_hint(text)
    language_mismatch = language_hint != "English/Latin script"

    length_reference = profile.get("article_word_count", {})
    coverage_reference = profile.get("vocabulary_coverage", {})
    lower_words = float(length_reference.get("p01", MIN_ARTICLE_WORDS))
    upper_words = float(length_reference.get("p99", max(2_000, article_words)))
    lower_coverage = float(coverage_reference.get("p01", 0.20))
    reasons: list[str] = []
    if article_words < MIN_ARTICLE_WORDS:
        reasons.append("Input contains too few words for the supported analysis path.")
    if language_mismatch:
        reasons.append("The packaged model supports English/Latin-script news only.")
    if article_words < lower_words or article_words > upper_words:
        reasons.append("Article length falls outside the central benchmark reference range.")
    if coverage < lower_coverage:
        reasons.append("Vocabulary coverage is below the benchmark reference range.")

    input_quality_inadequate = article_words < MIN_ARTICLE_WORDS or not tokens
    domain_mismatch = (
        article_words < lower_words or article_words > upper_words or coverage < lower_coverage
    )
    return InputDiagnostics(
        word_count=article_words,
        vocabulary_coverage=round(coverage, 6),
        out_of_vocabulary_rate=round(oov_rate, 6),
        language_hint=language_hint,
        language_mismatch=language_mismatch,
        domain_mismatch=domain_mismatch,
        input_quality_inadequate=input_quality_inadequate,
        review_reasons=tuple(reasons),
    )


def _indicator(name: str, current: float, reference: str, warning: bool, note: str) -> dict[str, Any]:
    return {
        "indicator": name,
        "current": round(float(current), 6),
        "reference": reference,
        "status": "Watch" if warning else "Within reference",
        "note": note,
    }


def assess_drift(
    analyses: pd.DataFrame,
    *,
    reference_profile: dict[str, Any] | None = None,
    total_attempts: int | None = None,
    invalid_attempts: int | None = None,
) -> dict[str, Any]:
    """Return privacy-safe aggregate distribution checks without retraining."""

    profile = reference_profile or load_reference_profile()
    minimum = int(profile.get("minimum_observations", MIN_DRIFT_OBSERVATIONS))
    observations = int(len(analyses))
    if observations < minimum:
        return {
            "status": "insufficient",
            "message": INSUFFICIENT_DRIFT_MESSAGE,
            "observations": observations,
            "minimum_observations": minimum,
            "indicators": [],
        }

    length_ref = profile.get("article_word_count", {})
    coverage_ref = profile.get("vocabulary_coverage", {})
    class_ref = profile.get("predicted_class_distribution", {})
    confidence_ref = profile.get("calibrated_confidence", {})
    current_length = float(pd.to_numeric(analyses["original_word_count"], errors="coerce").median())
    current_coverage = float(pd.to_numeric(analyses["vocabulary_coverage"], errors="coerce").mean())
    current_oov = float(pd.to_numeric(analyses["oov_rate"], errors="coerce").mean())
    current_misleading = float((analyses["predicted_class"] == "misleading").mean())
    current_confidence = float(pd.to_numeric(analyses["calibrated_confidence"], errors="coerce").mean())
    language_rate = float(pd.to_numeric(analyses["language_mismatch"], errors="coerce").fillna(0).mean())
    domain_rate = float(pd.to_numeric(analyses["domain_mismatch"], errors="coerce").fillna(0).mean())
    attempts = max(int(total_attempts or observations), observations)
    invalid = max(0, int(invalid_attempts or 0))
    invalid_rate = invalid / attempts if attempts else 0.0

    length_low = float(length_ref.get("p05", 0))
    length_high = float(length_ref.get("p95", float("inf")))
    coverage_floor = float(coverage_ref.get("p05", 0.0))
    expected_misleading = float(class_ref.get("misleading", 0.5))
    confidence_floor = float(confidence_ref.get("p05", 0.5))
    indicators = [
        _indicator(
            "Median article length",
            current_length,
            f"benchmark p05-p95: {length_low:.0f}-{length_high:.0f} words",
            current_length < length_low or current_length > length_high,
            "A shift may reflect a different content format; it does not prove model failure.",
        ),
        _indicator(
            "Mean vocabulary coverage",
            current_coverage,
            f"benchmark p05 floor: {coverage_floor:.1%}",
            current_coverage < coverage_floor,
            "Coverage uses the fitted TF-IDF unigram vocabulary.",
        ),
        _indicator(
            "Mean out-of-vocabulary rate",
            current_oov,
            f"derived ceiling: {1 - coverage_floor:.1%}",
            current_oov > 1 - coverage_floor,
            "Higher OOV can indicate new terms, languages or domains.",
        ),
        _indicator(
            "Higher-risk prediction share",
            current_misleading,
            f"benchmark reference: {expected_misleading:.1%}",
            abs(current_misleading - expected_misleading) > 0.20,
            "Class-balance change is a distribution signal, not proof of error.",
        ),
        _indicator(
            "Mean calibrated confidence",
            current_confidence,
            f"benchmark p05 floor: {confidence_floor:.1%}",
            current_confidence < confidence_floor,
            "Calibration is dataset-relative and does not verify facts.",
        ),
        _indicator(
            "Invalid-input rate",
            invalid_rate,
            "watch above 10%",
            invalid_rate > 0.10,
            "Only aggregate attempt counts are used; invalid article text is not retained.",
        ),
        _indicator(
            "Language-mismatch rate",
            language_rate,
            "watch above 10%",
            language_rate > 0.10,
            "Language detection is a lightweight script hint.",
        ),
        _indicator(
            "Domain-mismatch heuristic rate",
            domain_rate,
            "watch above 10%",
            domain_rate > 0.10,
            "This heuristic uses length and vocabulary coverage, not semantic domain labels.",
        ),
    ]
    warnings = sum(item["status"] == "Watch" for item in indicators)
    return {
        "status": "watch" if warnings else "within_reference",
        "message": (
            f"{warnings} aggregate indicator(s) require review. A warning indicates distributional "
            "change, not automatic model failure."
            if warnings
            else "Observed aggregate distributions remain within the configured reference checks."
        ),
        "observations": observations,
        "minimum_observations": minimum,
        "indicators": indicators,
    }
