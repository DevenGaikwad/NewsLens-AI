"""Tests for shared cleaning, statistics, and deterministic hashing."""

from src.text_preprocessor import clean_article_text, detect_language_hint, split_sentences, text_for_model
from src.utils import article_hash, compression_ratio, reading_time_minutes, word_count


def test_cleaning_removes_urls_controls_and_source_shortcuts() -> None:
    dirty = "LONDON (Reuters) - Reporting by Ana\x00. Visit https://example.com now."
    cleaned = clean_article_text(dirty)
    assert "https://" not in cleaned
    assert "\x00" not in cleaned
    assert "Reuters" not in cleaned
    assert "wire-service" in cleaned


def test_model_text_and_sentence_split_are_deterministic(sample_article: str) -> None:
    assert text_for_model("Price 25! PRICE 25!") == "price number price number"
    sentences = split_sentences(sample_article)
    assert len(sentences) >= 6
    assert sentences == split_sentences(sample_article)


def test_statistics_and_hash_normalisation(sample_article: str) -> None:
    assert word_count(sample_article) >= 100
    assert reading_time_minutes(sample_article) >= 1
    assert compression_ratio(100, 25) == 75.0
    assert article_hash("Hello   WORLD") == article_hash("hello world")
    assert detect_language_hint(sample_article) == "English/Latin script"
