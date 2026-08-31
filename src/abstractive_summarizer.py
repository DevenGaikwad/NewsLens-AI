"""Optional DistilBART summarizer with sentence-aware hierarchical chunking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

from .config import ABSTRACTIVE_MODEL_NAME
from .text_preprocessor import split_sentences
from .utils import compression_ratio, word_count


class AbstractiveDependencyError(RuntimeError):
    """Raised when optional transformer dependencies are unavailable."""


@dataclass(frozen=True)
class AbstractiveResult:
    summary: str
    method: str
    length: str
    original_word_count: int
    summary_word_count: int
    compression_ratio_pct: float
    processing_time_seconds: float
    chunk_count: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def load_transformer_pipeline(model_name: str = ABSTRACTIVE_MODEL_NAME) -> Any:
    """Load an abstractive pipeline; callers should cache this resource."""

    try:
        from transformers import pipeline
    except ImportError as exc:
        raise AbstractiveDependencyError(
            "Abstractive mode needs the optional transformer packages. "
            "Install requirements.txt or use Extractive mode."
        ) from exc
    return pipeline("summarization", model=model_name, device=-1)


def _sentence_chunks(text: str, max_words: int = 650, overlap_sentences: int = 1) -> list[str]:
    sentences = split_sentences(text)
    if not sentences:
        return []
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0
    for sentence in sentences:
        sentence_words = word_count(sentence)
        if current and current_words + sentence_words > max_words:
            chunks.append(" ".join(current))
            current = current[-overlap_sentences:] if overlap_sentences else []
            current_words = sum(word_count(item) for item in current)
        current.append(sentence)
        current_words += sentence_words
    if current:
        chunks.append(" ".join(current))
    return chunks


def _length_bounds(length: str, input_words: int) -> tuple[int, int]:
    ratios = {"Short": (0.08, 0.16), "Medium": (0.13, 0.24), "Detailed": (0.20, 0.34)}
    minimum_ratio, maximum_ratio = ratios.get(length, ratios["Medium"])
    minimum = max(24, min(90, int(input_words * minimum_ratio)))
    maximum = max(minimum + 10, min(180, int(input_words * maximum_ratio)))
    return minimum, maximum


def summarize_abstractive(text: str, summarizer: Any, length: str = "Medium") -> AbstractiveResult:
    """Summarize chunks, then re-summarize chunk summaries when necessary."""

    started = perf_counter()
    original_words = word_count(text)
    chunks = _sentence_chunks(text)
    if not chunks:
        return AbstractiveResult("", f"DistilBART ({ABSTRACTIVE_MODEL_NAME})", length, 0, 0, 0.0, 0.0, 0)

    partials: list[str] = []
    for chunk in chunks:
        minimum, maximum = _length_bounds(length, word_count(chunk))
        output = summarizer(
            chunk,
            min_length=minimum,
            max_length=maximum,
            do_sample=False,
            truncation=True,
        )
        partials.append(str(output[0]["summary_text"]).strip())

    combined = " ".join(partials)
    if len(partials) > 1 and word_count(combined) > 180:
        minimum, maximum = _length_bounds(length, word_count(combined))
        combined = str(
            summarizer(
                combined,
                min_length=minimum,
                max_length=maximum,
                do_sample=False,
                truncation=True,
            )[0]["summary_text"]
        ).strip()

    summary_words = word_count(combined)
    return AbstractiveResult(
        summary=combined,
        method=f"DistilBART ({ABSTRACTIVE_MODEL_NAME})",
        length=length,
        original_word_count=original_words,
        summary_word_count=summary_words,
        compression_ratio_pct=compression_ratio(original_words, summary_words),
        processing_time_seconds=round(perf_counter() - started, 4),
        chunk_count=len(chunks),
    )
