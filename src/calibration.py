"""Private Platt-calibration loading and inference-only score conversion."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
from typing import Any

import numpy as np

from .config import CALIBRATION_PATH, MODEL_PATH
from .utils import load_json


class CalibrationUnavailableError(RuntimeError):
    """Raised when calibrated confidence cannot be verified for the active model."""


@dataclass(frozen=True)
class CalibrationConfig:
    method: str
    coefficient: float
    intercept: float
    editorial_review_threshold: float
    model_sha256: str
    model_version: str
    calibration_rows: int
    threshold_policy_rows: int
    final_test_rows: int


def file_sha256(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_calibration(
    path: Path | str = CALIBRATION_PATH,
    *,
    model_path: Path | str = MODEL_PATH,
    verify_model: bool = True,
) -> CalibrationConfig:
    """Load calibration parameters and bind them to the expected model hash."""

    calibration_path = Path(path)
    if not calibration_path.exists():
        raise CalibrationUnavailableError(
            "The private confidence-calibration artefact is missing; calibrated confidence "
            "cannot be reported."
        )
    payload = load_json(calibration_path, {}) or {}
    required = {
        "method",
        "coefficient",
        "intercept",
        "editorial_review_threshold",
        "model_sha256",
        "model_version",
    }
    if not required.issubset(payload):
        raise CalibrationUnavailableError("The confidence-calibration artefact is incomplete.")
    threshold = float(payload["editorial_review_threshold"])
    if not 0.5 <= threshold < 1.0:
        raise CalibrationUnavailableError("The editorial-review threshold is outside [0.5, 1).")
    expected_hash = str(payload["model_sha256"])
    if verify_model:
        active_model_path = Path(model_path)
        if not active_model_path.exists() or file_sha256(active_model_path) != expected_hash:
            raise CalibrationUnavailableError(
                "The calibration parameters do not match the active model artefact."
            )
    return CalibrationConfig(
        method=str(payload["method"]),
        coefficient=float(payload["coefficient"]),
        intercept=float(payload["intercept"]),
        editorial_review_threshold=threshold,
        model_sha256=expected_hash,
        model_version=str(payload["model_version"]),
        calibration_rows=int(payload.get("calibration_rows", 0)),
        threshold_policy_rows=int(payload.get("threshold_policy_rows", 0)),
        final_test_rows=int(payload.get("final_test_rows", 0)),
    )


def decision_score(pipeline: Any, model_text: str) -> float:
    """Return a class-1 score suitable for the recorded Platt mapping."""

    if hasattr(pipeline, "decision_function"):
        return float(np.asarray(pipeline.decision_function([model_text])).ravel()[0])
    if not hasattr(pipeline, "predict_proba"):
        raise CalibrationUnavailableError("The active classifier exposes no calibratable score.")
    values = np.asarray(pipeline.predict_proba([model_text]), dtype=float)[0]
    classes = [int(value) for value in pipeline.classes_]
    positive = float(values[classes.index(1)])
    clipped = min(max(positive, 1e-8), 1 - 1e-8)
    return math.log(clipped / (1 - clipped))


def calibrated_misleading_probability(score: float, config: CalibrationConfig) -> float:
    linear = float(np.clip(config.coefficient * score + config.intercept, -35.0, 35.0))
    return 1.0 / (1.0 + math.exp(-linear))


def calibrated_probability_pair(
    pipeline: Any,
    model_text: str,
    config: CalibrationConfig,
) -> tuple[float, float]:
    misleading = calibrated_misleading_probability(decision_score(pipeline, model_text), config)
    return 1.0 - misleading, misleading
