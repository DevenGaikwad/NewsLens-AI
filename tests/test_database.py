"""SQLite CRUD, search/filter, and duplicate-hash integration tests."""

from src.database import (
    clear_history,
    delete_analysis,
    get_analysis,
    insert_analysis,
    list_analyses,
    update_editorial_review,
)
from src.utils import article_hash
from src.session_history import history_mode, scoped_history_path


def _record() -> dict[str, object]:
    return {
        "timestamp": "2026-07-17T00:00:00+00:00",
        "input_type": "Direct text",
        "source_url": "",
        "source_domain": "example.test",
        "article_title": "Deterministic database test",
        "article_hash": article_hash("database test article"),
        "original_word_count": 100,
        "summary_method": "TF-IDF centroid extractive",
        "summary_length": "Short",
        "generated_summary": "A compact deterministic summary.",
        "prediction_label": "Editorial review required",
        "reliable_probability": 0.52,
        "misleading_probability": 0.48,
        "confidence_band": "Review",
        "model_version": "test-v1",
        "processing_time": 0.25,
    }


def test_database_crud_and_duplicate_detection(tmp_path) -> None:
    path = tmp_path / "history.db"
    first_id, duplicate = insert_analysis(_record(), path)
    second_id, duplicate_again = insert_analysis(_record(), path)
    assert duplicate is False
    assert duplicate_again is True
    assert first_id == second_id
    assert get_analysis(first_id, path)["article_title"] == "Deterministic database test"
    assert len(list_analyses(search="database", path=path)) == 1
    assert delete_analysis(first_id, path)
    assert get_analysis(first_id, path) is None


def test_clear_history(tmp_path, monkeypatch) -> None:
    path = tmp_path / "history.db"
    insert_analysis(_record(), path)
    assert clear_history(path) == 1
    assert list_analyses(path=path).empty
    assert scoped_history_path("visitor-a", tmp_path) != scoped_history_path(
        "visitor-b", tmp_path
    )
    monkeypatch.delenv("NEWSLENS_HISTORY_MODE", raising=False)
    assert history_mode() == "session"
    monkeypatch.setenv("NEWSLENS_HISTORY_MODE", "unexpected")
    assert history_mode() == "session"


def test_editorial_review_update_is_scoped_and_validated(tmp_path) -> None:
    path = tmp_path / "history.db"
    analysis_id, _ = insert_analysis(_record(), path)
    assert update_editorial_review(
        analysis_id,
        review_status="Inconclusive",
        reviewer_notes="The available evidence does not resolve the claim.",
        supporting_source_urls="https://example.test/source-one",
        final_editorial_assessment="Escalate to a specialist editor.",
        path=path,
    )
    saved = get_analysis(analysis_id, path)
    assert saved["review_status"] == "Inconclusive"
    assert saved["supporting_source_urls"] == "https://example.test/source-one"
    assert saved["review_updated_at"]
