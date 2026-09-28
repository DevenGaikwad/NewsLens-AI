"""Central project configuration and portable filesystem paths."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
RESULTS_DIR = REPORTS_DIR / "results"
FIGURES_DIR = REPORTS_DIR / "figures"
DIAGRAMS_DIR = REPORTS_DIR / "diagrams"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
DATABASE_DIR = PROJECT_ROOT / "database"

MODEL_PATH = Path(
    os.getenv("NEWSLENS_MODEL_PATH", MODELS_DIR / "newslens_synthetic_pipeline.joblib")
)
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"
CALIBRATION_PATH = Path(
    os.getenv(
        "NEWSLENS_CALIBRATION_PATH", MODELS_DIR / "newslens_synthetic_calibration.json"
    )
)
MODEL_REFERENCE_PROFILE_PATH = REPORTS_DIR / "model_reference_profile.json"
DATABASE_PATH = Path(os.getenv("NEWSLENS_DATABASE_PATH", DATABASE_DIR / "analysis_history.db"))

MODEL_VERSION = "newslens-synthetic-tfidf-v1.0.0"
EXPECTED_PACKAGED_CHECKS = 154
RANDOM_SEED = 42
MIN_ARTICLE_WORDS = 40
MIN_DRIFT_OBSERVATIONS = 20
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 15
MAX_URL_LENGTH = 2048
MAX_REDIRECTS = 5
MAX_ARTICLE_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 200
MAX_EXTRACTED_TEXT_CHARS = 2_000_000
UNCERTAIN_THRESHOLD = 0.60
HIGH_CONFIDENCE_THRESHOLD = 0.80
DISCLAIMER = (
    "This synthetic-benchmark consistency signal compares the visible Reference note and "
    "Article account fields. It does not verify real-world facts or determine truth."
)
FIELDS_AGREE_PROBABILITY_LABEL = "Fields agree - calibrated probability"
FIELDS_CONFLICT_PROBABILITY_LABEL = "Fields conflict - calibrated probability"
REFERENCE_COMPARISON_CONFIDENCE_LABEL = "Reference-comparison confidence"
CALIBRATED_SCORE_EXPLANATION = (
    '"Fields agree" and "Fields conflict" are calibrated probabilities for the two synthetic '
    "benchmark classes learned from visible Reference note and Article account comparison "
    "patterns. They are not truth probabilities."
)
CALIBRATED_CONFIDENCE_EXPLANATION = (
    "Reference-comparison confidence is the model's calibrated confidence in its selected "
    "synthetic consistency class. It is not factual certainty."
)
EDITORIAL_REVIEW_EXPLANATION = (
    "Editorial review can be required by unsupported structure, scope controls, or the review "
    "policy even when numerical class probabilities are available."
)
OUT_OF_SCOPE_EXPLANATION = (
    "Outside supported automatic comparison scope: ordinary prose, missing or repeated fields, "
    "or a model agreement score that conflicts with a visible field difference requires human "
    "review. Directional probabilities are withheld in these cases. The model does not "
    "establish factual credibility for external articles."
)

LOWER_RISK_OUTCOME = "Synthetic ledger-consistent pattern indicated"
HIGHER_RISK_OUTCOME = "Synthetic ledger-contradicting pattern indicated"
REVIEW_REQUIRED_OUTCOME = "Editorial review required"
REFERENCE_AGREEMENT_OUTCOME = "The article fields agree with the supplied reference"
REFERENCE_CONFLICT_OUTCOME = "The article fields conflict with the supplied reference"

PROJECT_AUTHOR = "Deven Sachin Gaikwad"
COPYRIGHT_NOTICE = "© 2026 Deven Sachin Gaikwad. All Rights Reserved."
PUBLIC_AUTHOR = "Deven Gaikwad"
PUBLIC_COPYRIGHT_NOTICE = "© 2026 · All rights reserved"


def ensure_runtime_directories() -> None:
    """Create directories written to by the application at runtime."""

    for directory in (MODELS_DIR, RESULTS_DIR, DATABASE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
