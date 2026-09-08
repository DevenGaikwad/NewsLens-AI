"""Tests for shared cleaning, statistics, and deterministic hashing."""

import re
from time import perf_counter

import pytest

from src.text_preprocessor import clean_article_text, detect_language_hint, split_sentences, text_for_model
from src.utils import article_hash, compression_ratio, reading_time_minutes, word_count


def test_cleaning_removes_urls_controls_and_source_shortcuts() -> None:
    dirty = "LONDON (Reuters) - Reporting by Ana\x00. Visit https://example.com now."
    cleaned = clean_article_text(dirty)
    assert "https://" not in cleaned
    assert "\x00" not in cleaned
    assert "Reuters" not in cleaned
    assert "wire-service" in cleaned


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("", "", id="empty"),
        pytest.param("  Ordinary sentence.  ", "Ordinary sentence.", id="single-line"),
        pytest.param("Alpha\nBeta", "Alpha\nBeta", id="lf"),
        pytest.param("Alpha\r\nBeta", "Alpha\nBeta", id="crlf"),
        pytest.param("Alpha\rBeta", "Alpha\nBeta", id="standalone-cr"),
        pytest.param("Alpha \t \n \t Beta", "Alpha\nBeta", id="boundary-whitespace"),
        pytest.param("Alpha\f\vBeta", "Alpha Beta", id="form-feed-and-vertical-tab"),
        pytest.param("\u2003Alpha\u2002\n\u3000Beta\u2009", "Alpha\nBeta", id="unicode-boundaries"),
        pytest.param("Alpha\u2003Beta", "Alpha\u2003Beta", id="unicode-internal"),
        pytest.param("Alpha\n\n\n\nBeta", "Alpha\n\nBeta", id="blank-line-limit"),
        pytest.param("\n \n Alpha \n \n", "Alpha", id="leading-and-trailing"),
        pytest.param(
            "First paragraph.\n\nSecond paragraph!\n\n\nThird paragraph?",
            "First paragraph.\n\nSecond paragraph!\n\nThird paragraph?",
            id="paragraphs-and-punctuation",
        ),
        pytest.param("Already normalized.\nNext line.", "Already normalized.\nNext line.", id="normalized"),
    ],
)
def test_cleaning_normalizes_line_boundaries(raw: str, expected: str) -> None:
    assert clean_article_text(raw, remove_source_markers=False) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "Alpha\r\nBeta",
        "Alpha\rBeta",
        "Alpha \t\n\n \u2003Beta",
        "First.\n\n\nSecond!",
    ],
)
def test_cleaning_line_normalization_is_idempotent(raw: str) -> None:
    normalized = clean_article_text(raw, remove_source_markers=False)
    assert clean_article_text(normalized, remove_source_markers=False) == normalized


def test_line_normalization_preserves_sentence_splitting() -> None:
    raw = "First sentence.\r\nSecond sentence!\rThird sentence?"
    expected = ["First sentence.", "Second sentence!", "Third sentence?"]

    normalized = clean_article_text(raw, remove_source_markers=False)
    assert split_sentences(raw) == expected
    assert split_sentences(normalized) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("", [], id="empty"),
        pytest.param("One ordinary sentence.", ["One ordinary sentence."], id="single-sentence"),
        pytest.param(
            "First sentence. Second sentence? Third sentence! Fourth clause; Final clause.",
            ["First sentence.", "Second sentence?", "Third sentence!", "Fourth clause;", "Final clause."],
            id="period-question-exclamation-semicolon",
        ),
        pytest.param("Really?! Next... Another!", ["Really?!", "Next...", "Another!"], id="repeated-punctuation"),
        pytest.param("First. Second?", ["First.", "Second?"], id="one-space"),
        pytest.param("First.     Second?", ["First.", "Second?"], id="multiple-spaces"),
        pytest.param(
            "First.\tSecond?\nThird!\u2003Fourth.",
            ["First.", "Second?", "Third!", "Fourth."],
            id="ascii-and-unicode-whitespace",
        ),
        pytest.param(
            "Dr. Smith met Prof. Jones. Next topic.",
            ["Dr.", "Smith met Prof.", "Jones.", "Next topic."],
            id="existing-abbreviation-behaviour",
        ),
        pytest.param(
            "J. Smith paid 3.14 dollars. Next item.",
            ["J.", "Smith paid 3.14 dollars.", "Next item."],
            id="initial-and-decimal",
        ),
        pytest.param(
            'First. "Second starts." Third.',
            ["First.", '"Second starts." Third.'],
            id="quoted-sentence",
        ),
        pytest.param(
            "First. (Second begins.) Third.",
            ["First.", "(Second begins.) Third."],
            id="parenthesized-sentence",
        ),
        pytest.param(
            "Café résumé. Über alles? Ελληνικά κείμενο. Next.",
            ["Café résumé. Über alles? Ελληνικά κείμενο.", "Next."],
            id="unicode-content",
        ),
        pytest.param(
            "This text has no sentence-ending punctuation",
            ["This text has no sentence-ending punctuation"],
            id="no-boundary",
        ),
    ],
)
def test_sentence_boundary_semantics_are_preserved(raw: str, expected: list[str]) -> None:
    assert split_sentences(raw) == expected


def test_sentence_boundary_input_is_normalized_to_single_spaces() -> None:
    raw = "First.\t \n\u2003Second?\r\n\tThird!"
    cleaned = clean_article_text(raw, remove_source_markers=False)
    normalized = re.sub(r"\s+", " ", cleaned)

    assert normalized == "First. Second? Third!"
    assert all(char == " " or not char.isspace() for char in normalized)
    assert "  " not in normalized
    assert split_sentences(raw) == split_sentences(normalized)


def test_sentence_order_and_repeat_preprocessing_are_stable() -> None:
    raw = "Alpha first.\r\nBeta second?\n\nGamma third!"
    expected = ["Alpha first.", "Beta second?", "Gamma third!"]

    first_pass = split_sentences(raw)
    assert first_pass == expected
    assert split_sentences(" ".join(first_pass)) == expected


def test_sentence_split_preserves_a_very_long_sentence() -> None:
    sentence = "A" * 250_000
    assert split_sentences(sentence) == [sentence]


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param("Start." + " " * 300_000 + "lowercase", id="spaces-after-punctuation"),
        pytest.param("word" + "\t" * 300_000 + "word", id="whitespace-without-punctuation"),
        pytest.param("Dr. A. " * 40_000, id="abbreviation-like-fragments"),
        pytest.param("Really?!     " * 30_000, id="punctuation-and-spaces"),
        pytest.param("Sentence one. Sentence two? " * 20_000, id="normalized-article"),
        pytest.param("Alpha.\u2003Beta?\u2009" * 30_000, id="unicode-whitespace"),
        pytest.param("x" * 500_000, id="no-split-point"),
        pytest.param("A. B? C! " * 40_000, id="alternating-boundaries"),
    ],
)
def test_sentence_split_handles_large_adversarial_inputs_without_delay(payload: str) -> None:
    started = perf_counter()
    sentences = split_sentences(payload)
    elapsed = perf_counter() - started

    assert isinstance(sentences, list)
    assert elapsed < 5.0


def test_sentence_split_runtime_growth_is_bounded() -> None:
    durations: list[float] = []
    for size in (50_000, 100_000, 200_000):
        samples = []
        payload = "Start." + " " * size + "lowercase"
        for _ in range(3):
            started = perf_counter()
            assert split_sentences(payload) == ["Start. lowercase"]
            samples.append(perf_counter() - started)
        durations.append(min(samples))

    for previous, current in zip(durations, durations[1:]):
        assert current <= previous * 3.5 + 0.05


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param("\r" * 100_000, id="carriage-return-only"),
        pytest.param(" " * 500_000, id="spaces-without-newline"),
        pytest.param("\t" * 500_000, id="tabs-without-newline"),
        pytest.param((" \n\t") * 100_000, id="alternating-whitespace-newline"),
        pytest.param("\n" * 300_000, id="blank-line-run"),
        pytest.param("\r\n" * 150_000, id="large-crlf"),
        pytest.param("Ordinary article sentence with punctuation. " * 20_000, id="ordinary-article"),
        pytest.param("\u2003" * 100_000, id="unicode-whitespace"),
    ],
)
def test_cleaning_handles_large_adversarial_inputs_without_delay(payload: str) -> None:
    started = perf_counter()
    cleaned = clean_article_text(payload, remove_source_markers=False)
    elapsed = perf_counter() - started

    assert len(cleaned) <= len(payload)
    assert elapsed < 3.0


def test_carriage_return_runtime_growth_is_bounded() -> None:
    durations: list[float] = []
    for size in (25_000, 50_000, 100_000):
        samples = []
        for _ in range(3):
            started = perf_counter()
            assert clean_article_text("\r" * size, remove_source_markers=False) == ""
            samples.append(perf_counter() - started)
        durations.append(min(samples))

    for previous, current in zip(durations, durations[1:]):
        assert current <= previous * 3.5 + 0.05


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
