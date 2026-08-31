"""Tests for short, long, empty, and ordered extractive summaries."""

from src.extractive_summarizer import summarize_extractive


def test_extractive_summary_compresses_and_preserves_order(sample_article: str) -> None:
    result = summarize_extractive(sample_article, "Short")
    assert result.summary
    assert 0 < result.summary_word_count < result.original_word_count
    assert result.compression_ratio_pct > 0
    positions = [sample_article.index(sentence.strip()) for sentence in result.summary.split(". ") if sentence.strip() in sample_article]
    assert positions == sorted(positions)


def test_summary_length_control(sample_article: str) -> None:
    short = summarize_extractive(sample_article, "Short")
    detailed = summarize_extractive(sample_article, "Detailed")
    assert detailed.summary_word_count >= short.summary_word_count


def test_empty_and_long_inputs_do_not_crash(sample_article: str) -> None:
    assert summarize_extractive("", "Medium").summary == ""
    long_result = summarize_extractive(" ".join([sample_article] * 30), "Medium")
    assert long_result.summary
    assert long_result.selected_sentence_count <= 6
