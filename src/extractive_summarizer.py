"""CPU-friendly extractive summarization using TF-IDF centroid ranking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .text_preprocessor import split_sentences
from .utils import compression_ratio, word_count


@dataclass(frozen=True)
class SummaryResult:
    """Serializable summarization response."""

    summary: str
    method: str
    length: str
    original_word_count: int
    summary_word_count: int
    compression_ratio_pct: float
    processing_time_seconds: float
    selected_sentence_count: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


LENGTH_FRACTIONS = {"Short": 0.18, "Medium": 0.30, "Detailed": 0.45}
MAX_SENTENCES = {"Short": 3, "Medium": 6, "Detailed": 10}


def _target_sentence_count(total: int, length: str) -> int:
    fraction = LENGTH_FRACTIONS.get(length, LENGTH_FRACTIONS["Medium"])
    cap = MAX_SENTENCES.get(length, MAX_SENTENCES["Medium"])
    target = max(1, int(round(total * fraction)))
    return min(total, cap, target)


def summarize_extractive(text: str, length: str = "Medium") -> SummaryResult:
    """Summarize by selecting sentences nearest the document TF-IDF centroid.

    A mild lead-position and information-density bonus is used because news
    writing commonly places high-level facts near the beginning. Selected
    sentences are restored to their original order for coherence.
    """

    started = perf_counter()
    sentences = [sentence for sentence in split_sentences(text) if word_count(sentence) >= 4]
    original_words = word_count(text)
    if not sentences:
        return SummaryResult("", "TF-IDF centroid extractive", length, original_words, 0, 0.0, 0.0, 0)
    if len(sentences) <= 2:
        summary = " ".join(sentences)
        elapsed = perf_counter() - started
        return SummaryResult(
            summary,
            "TF-IDF centroid extractive",
            length,
            original_words,
            word_count(summary),
            compression_ratio(original_words, word_count(summary)),
            round(elapsed, 4),
            len(sentences),
        )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    try:
        matrix = vectorizer.fit_transform(sentences)
        centroid = np.asarray(matrix.mean(axis=0)).ravel()
        norms = np.sqrt(matrix.multiply(matrix).sum(axis=1)).A1
        centroid_norm = float(np.linalg.norm(centroid)) or 1.0
        similarity = np.asarray(matrix @ centroid).ravel() / (norms * centroid_norm + 1e-12)
    except ValueError:
        similarity = np.linspace(1.0, 0.25, num=len(sentences))

    positions = np.arange(len(sentences), dtype=float)
    lead_bonus = 0.12 * np.exp(-positions / max(1, len(sentences) * 0.25))
    lengths = np.array([word_count(sentence) for sentence in sentences], dtype=float)
    density_bonus = 0.04 * np.clip(lengths / 24.0, 0.0, 1.0)
    scores = similarity + lead_bonus + density_bonus

    target = _target_sentence_count(len(sentences), length)
    chosen = sorted(np.argsort(scores)[-target:].tolist())
    summary = " ".join(sentences[index] for index in chosen)
    summary_words = word_count(summary)
    elapsed = perf_counter() - started
    return SummaryResult(
        summary=summary,
        method="TF-IDF centroid extractive",
        length=length,
        original_word_count=original_words,
        summary_word_count=summary_words,
        compression_ratio_pct=compression_ratio(original_words, summary_words),
        processing_time_seconds=round(elapsed, 4),
        selected_sentence_count=len(chosen),
    )
