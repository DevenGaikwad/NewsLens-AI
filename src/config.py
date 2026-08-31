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

MODEL_PATH = Path(os.getenv("NEWSLENS_MODEL_PATH", MODELS_DIR / "fake_news_pipeline.joblib"))
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"
CALIBRATION_PATH = Path(
    os.getenv("NEWSLENS_CALIBRATION_PATH", MODELS_DIR / "confidence_calibration.json")
)
MODEL_REFERENCE_PROFILE_PATH = REPORTS_DIR / "model_reference_profile.json"
DATABASE_PATH = Path(os.getenv("NEWSLENS_DATABASE_PATH", DATABASE_DIR / "analysis_history.db"))

MODEL_VERSION = "isot-tfidf-lr-v1.0.0"
EXPECTED_PACKAGED_CHECKS = 56
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
ABSTRACTIVE_MODEL_NAME = os.getenv(
    "NEWSLENS_ABSTRACTIVE_MODEL", "sshleifer/distilbart-cnn-6-6"
)

DISCLAIMER = (
    "This result is a machine-learning risk signal. It is not independent confirmation "
    "that an article is factually true or false."
)

LOWER_RISK_OUTCOME = "Lower misleading-content risk indicated"
HIGHER_RISK_OUTCOME = "Higher misleading-content risk indicated"
REVIEW_REQUIRED_OUTCOME = "Editorial review required"

PROJECT_AUTHOR = "Deven Sachin Gaikwad"
COPYRIGHT_NOTICE = "© 2026 Deven Sachin Gaikwad. All Rights Reserved."


def ensure_runtime_directories() -> None:
    """Create directories written to by the application at runtime."""

    for directory in (MODELS_DIR, RESULTS_DIR, DATABASE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
