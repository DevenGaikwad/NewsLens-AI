"""SQLite persistence for local, privacy-conscious analysis history."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from .config import DATABASE_PATH
from .editorial_review import REVIEW_STATUSES, validate_review_update
from .utils import utc_now_iso


SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    input_type TEXT NOT NULL,
    source_url TEXT,
    source_domain TEXT,
    article_title TEXT,
    article_hash TEXT NOT NULL UNIQUE,
    original_word_count INTEGER NOT NULL CHECK (original_word_count >= 0),
    summary_method TEXT NOT NULL,
    summary_length TEXT NOT NULL,
    generated_summary TEXT NOT NULL,
    prediction_label TEXT NOT NULL,
    predicted_class TEXT NOT NULL DEFAULT 'reliable',
    reliable_probability REAL NOT NULL CHECK (reliable_probability BETWEEN 0 AND 1),
    misleading_probability REAL NOT NULL CHECK (misleading_probability BETWEEN 0 AND 1),
    calibrated_confidence REAL NOT NULL DEFAULT 0.5 CHECK (calibrated_confidence BETWEEN 0 AND 1),
    confidence_band TEXT NOT NULL,
    calibration_method TEXT NOT NULL DEFAULT 'Unavailable',
    editorial_review_threshold REAL NOT NULL DEFAULT 1.0 CHECK (editorial_review_threshold BETWEEN 0.5 AND 1),
    review_required INTEGER NOT NULL DEFAULT 1 CHECK (review_required IN (0, 1)),
    review_reason TEXT NOT NULL DEFAULT '',
    review_status TEXT NOT NULL DEFAULT 'Pending review',
    reviewer_notes TEXT NOT NULL DEFAULT '',
    supporting_source_urls TEXT NOT NULL DEFAULT '',
    final_editorial_assessment TEXT NOT NULL DEFAULT '',
    review_updated_at TEXT,
    vocabulary_coverage REAL NOT NULL DEFAULT 0 CHECK (vocabulary_coverage BETWEEN 0 AND 1),
    oov_rate REAL NOT NULL DEFAULT 1 CHECK (oov_rate BETWEEN 0 AND 1),
    language_mismatch INTEGER NOT NULL DEFAULT 0 CHECK (language_mismatch IN (0, 1)),
    domain_mismatch INTEGER NOT NULL DEFAULT 0 CHECK (domain_mismatch IN (0, 1)),
    model_version TEXT NOT NULL,
    processing_time REAL NOT NULL CHECK (processing_time >= 0)
);
CREATE INDEX IF NOT EXISTS idx_analyses_timestamp ON analyses(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_label ON analyses(prediction_label);
"""

INSERT_SQL = """
INSERT INTO analyses (
    timestamp, input_type, source_url, source_domain, article_title, article_hash,
    original_word_count, summary_method, summary_length, generated_summary,
    prediction_label, predicted_class, reliable_probability, misleading_probability,
    calibrated_confidence, confidence_band, calibration_method,
    editorial_review_threshold, review_required, review_reason, review_status,
    reviewer_notes, supporting_source_urls, final_editorial_assessment, review_updated_at,
    vocabulary_coverage, oov_rate, language_mismatch, domain_mismatch,
    model_version, processing_time
) VALUES (
    :timestamp, :input_type, :source_url, :source_domain, :article_title, :article_hash,
    :original_word_count, :summary_method, :summary_length, :generated_summary,
    :prediction_label, :predicted_class, :reliable_probability, :misleading_probability,
    :calibrated_confidence, :confidence_band, :calibration_method,
    :editorial_review_threshold, :review_required, :review_reason, :review_status,
    :reviewer_notes, :supporting_source_urls, :final_editorial_assessment, :review_updated_at,
    :vocabulary_coverage, :oov_rate, :language_mismatch, :domain_mismatch,
    :model_version, :processing_time
)
"""


DEFAULT_ANALYSIS_FIELDS: dict[str, Any] = {
    "predicted_class": "reliable",
    "calibrated_confidence": 0.5,
    "calibration_method": "Unavailable",
    "editorial_review_threshold": 1.0,
    "review_required": 1,
    "review_reason": "Calibration or quality evidence was not recorded.",
    "review_status": "Pending review",
    "reviewer_notes": "",
    "supporting_source_urls": "",
    "final_editorial_assessment": "",
    "review_updated_at": None,
    "vocabulary_coverage": 0.0,
    "oov_rate": 1.0,
    "language_mismatch": 0,
    "domain_mismatch": 0,
}


MIGRATION_COLUMNS: dict[str, str] = {
    "predicted_class": "TEXT NOT NULL DEFAULT 'reliable'",
    "calibrated_confidence": "REAL NOT NULL DEFAULT 0.5",
    "calibration_method": "TEXT NOT NULL DEFAULT 'Unavailable'",
    "editorial_review_threshold": "REAL NOT NULL DEFAULT 1.0",
    "review_required": "INTEGER NOT NULL DEFAULT 1",
    "review_reason": "TEXT NOT NULL DEFAULT ''",
    "review_status": "TEXT NOT NULL DEFAULT 'Pending review'",
    "reviewer_notes": "TEXT NOT NULL DEFAULT ''",
    "supporting_source_urls": "TEXT NOT NULL DEFAULT ''",
    "final_editorial_assessment": "TEXT NOT NULL DEFAULT ''",
    "review_updated_at": "TEXT",
    "vocabulary_coverage": "REAL NOT NULL DEFAULT 0",
    "oov_rate": "REAL NOT NULL DEFAULT 1",
    "language_mismatch": "INTEGER NOT NULL DEFAULT 0",
    "domain_mismatch": "INTEGER NOT NULL DEFAULT 0",
}


def connect(path: Path | str = DATABASE_PATH) -> sqlite3.Connection:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(path: Path | str = DATABASE_PATH) -> None:
    with connect(path) as connection:
        connection.executescript(SCHEMA)
        columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(analyses)").fetchall()
        }
        for name, definition in MIGRATION_COLUMNS.items():
            if name not in columns:
                connection.execute(f"ALTER TABLE analyses ADD COLUMN {name} {definition}")
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_review_status ON analyses(review_status)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_review_required ON analyses(review_required)"
        )


def insert_analysis(record: dict[str, Any], path: Path | str = DATABASE_PATH) -> tuple[int, bool]:
    """Insert an analysis; return existing id and True when it is a duplicate."""

    initialize_database(path)
    payload = {**DEFAULT_ANALYSIS_FIELDS, **record}
    with connect(path) as connection:
        try:
            cursor = connection.execute(INSERT_SQL, payload)
            return int(cursor.lastrowid), False
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed" not in str(exc):
                raise
            row = connection.execute(
                "SELECT analysis_id FROM analyses WHERE article_hash = ?",
                (payload["article_hash"],),
            ).fetchone()
            return int(row["analysis_id"]), True


def update_editorial_review(
    analysis_id: int,
    *,
    review_status: str,
    reviewer_notes: object,
    supporting_source_urls: object,
    final_editorial_assessment: object,
    path: Path | str = DATABASE_PATH,
) -> bool:
    """Validate and save one human review in the caller's scoped database."""

    if review_status not in REVIEW_STATUSES:
        raise ValueError("Unsupported editorial-review status.")
    values = validate_review_update(
        review_status=review_status,
        reviewer_notes=reviewer_notes,
        supporting_source_urls=supporting_source_urls,
        final_editorial_assessment=final_editorial_assessment,
    )
    initialize_database(path)
    with connect(path) as connection:
        cursor = connection.execute(
            """
            UPDATE analyses
               SET review_status = :review_status,
                   reviewer_notes = :reviewer_notes,
                   supporting_source_urls = :supporting_source_urls,
                   final_editorial_assessment = :final_editorial_assessment,
                   review_updated_at = :review_updated_at
             WHERE analysis_id = :analysis_id
            """,
            {**values, "review_updated_at": utc_now_iso(), "analysis_id": int(analysis_id)},
        )
        return cursor.rowcount > 0


def list_analyses(
    search: str = "",
    label: str = "All",
    limit: int = 500,
    path: Path | str = DATABASE_PATH,
) -> pd.DataFrame:
    initialize_database(path)
    clauses: list[str] = []
    params: list[Any] = []
    if search.strip():
        clauses.append("(article_title LIKE ? OR source_domain LIKE ? OR generated_summary LIKE ?)")
        value = f"%{search.strip()}%"
        params.extend([value, value, value])
    if label != "All":
        clauses.append("prediction_label = ?")
        params.append(label)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"SELECT * FROM analyses {where} ORDER BY timestamp DESC LIMIT ?"
    params.append(max(1, min(limit, 5000)))
    with connect(path) as connection:
        return pd.read_sql_query(query, connection, params=params)


def get_analysis(analysis_id: int, path: Path | str = DATABASE_PATH) -> dict[str, Any] | None:
    initialize_database(path)
    with connect(path) as connection:
        row = connection.execute(
            "SELECT * FROM analyses WHERE analysis_id = ?", (int(analysis_id),)
        ).fetchone()
    return dict(row) if row else None


def delete_analysis(analysis_id: int, path: Path | str = DATABASE_PATH) -> bool:
    initialize_database(path)
    with connect(path) as connection:
        cursor = connection.execute(
            "DELETE FROM analyses WHERE analysis_id = ?", (int(analysis_id),)
        )
        return cursor.rowcount > 0


def clear_history(path: Path | str = DATABASE_PATH) -> int:
    initialize_database(path)
    with connect(path) as connection:
        cursor = connection.execute("DELETE FROM analyses")
        return cursor.rowcount
