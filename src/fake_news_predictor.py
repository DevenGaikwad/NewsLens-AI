"""Saved-pipeline loading, calibrated risk signals, and responsible abstention."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import joblib

from .calibration import (
    CalibrationConfig,
    CalibrationUnavailableError,
    calibrated_probability_pair,
    decision_score,
    load_calibration,
)
from .config import (
    HIGHER_RISK_OUTCOME,
    LOWER_RISK_OUTCOME,
    MODEL_METADATA_PATH,
    MODEL_PATH,
    MODEL_VERSION,
    REVIEW_REQUIRED_OUTCOME,
)
from .explainability import explain_linear_prediction
from .model_diagnostics import InputDiagnostics
from .text_preprocessor import text_for_model
from .utils import load_json


class ModelLoadError(RuntimeError):
    """Raised when the packaged model is missing or incompatible."""


@dataclass(frozen=True)
class PredictionResult:
    predicted_class: str
    display_label: str
    reliable_probability: float
    misleading_probability: float
    confidence: float
    confidence_band: str
    calibration_method: str
    calibration_status: str
    editorial_review_threshold: float
    review_required: bool
    review_reason: str
    model_version: str
    processing_time_seconds: float
    explanation: dict[str, list[dict[str, float | str]]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_model(path: Path | str = MODEL_PATH) -> Any:
    """Load a fitted scikit-learn pipeline without retraining."""

    model_path = Path(path)
    if not model_path.exists():
        raise ModelLoadError(
            "The trained model file is missing. Run: python training/train_fake_news_models.py"
        )
    try:
        pipeline = joblib.load(model_path)
    except Exception as exc:
        raise ModelLoadError("The saved model could not be loaded.") from exc
    if not hasattr(pipeline, "predict") or not hasattr(pipeline, "named_steps"):
        raise ModelLoadError("The saved object is not a compatible scikit-learn pipeline.")
    return pipeline


def predict_credibility(
    text: str,
    pipeline: Any,
    *,
    calibration: CalibrationConfig | None = None,
    diagnostics: InputDiagnostics | None = None,
) -> PredictionResult:
    """Predict the cleaned article, calibrate confidence, and abstain when needed."""

    started = perf_counter()
    model_text = text_for_model(text)
    calibration_status = "verified"
    review_reasons: list[str] = []
    try:
        active_calibration = calibration or load_calibration()
        reliable, misleading = calibrated_probability_pair(
            pipeline, model_text, active_calibration
        )
        method = active_calibration.method
        threshold = active_calibration.editorial_review_threshold
    except CalibrationUnavailableError as exc:
        score = decision_score(pipeline, model_text)
        predicted_from_score = "misleading" if score >= 0 else "reliable"
        reliable = 0.5
        misleading = 0.5
        method = "Unavailable"
        threshold = 1.0
        calibration_status = "unavailable"
        review_reasons.append(str(exc))

    if calibration_status == "verified":
        predicted = "misleading" if misleading >= 0.5 else "reliable"
    else:
        predicted = predicted_from_score
    confidence = misleading if predicted == "misleading" else reliable
    if confidence < threshold:
        review_reasons.append(
            f"Calibrated confidence {confidence:.1%} is below the validation-selected "
            f"{threshold:.0%} review threshold."
        )
    if diagnostics is not None:
        review_reasons.extend(diagnostics.review_reasons)
    review_required = bool(review_reasons)
    if review_required:
        display = REVIEW_REQUIRED_OUTCOME
        band = "Review"
    else:
        display = HIGHER_RISK_OUTCOME if predicted == "misleading" else LOWER_RISK_OUTCOME
        band = "High" if confidence >= 0.90 else "Moderate"
    try:
        explanation = explain_linear_prediction(pipeline, model_text)
    except (KeyError, ValueError):
        explanation = {"supports_misleading": [], "supports_reliable": []}
    metadata = load_json(MODEL_METADATA_PATH, {}) or {}
    version = str(metadata.get("model_version", MODEL_VERSION))
    return PredictionResult(
        predicted_class=predicted,
        display_label=display,
        reliable_probability=round(reliable, 4),
        misleading_probability=round(misleading, 4),
        confidence=round(confidence, 4),
        confidence_band=band,
        calibration_method=method,
        calibration_status=calibration_status,
        editorial_review_threshold=round(threshold, 4),
        review_required=review_required,
        review_reason=" ".join(dict.fromkeys(review_reasons)),
        model_version=version,
        processing_time_seconds=round(perf_counter() - started, 4),
        explanation=explanation,
    )
