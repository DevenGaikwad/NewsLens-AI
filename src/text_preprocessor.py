"""Text normalisation shared by training and inference."""

from __future__ import annotations

import html
import re


REUTERS_LEAD = re.compile(
    r"^\s*[A-Z][A-Z .,'/-]{1,45}\s*\(Reuters\)\s*[-–—]\s*",
    flags=re.IGNORECASE,
)
WIRE_MARKERS = re.compile(
    r"\b(?:reuters|associated press|ap photo|reporting by|editing by)\b",
    flags=re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
CONTROL_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_article_text(text: str, remove_source_markers: bool = True) -> str:
    """Clean article text without stemming away information needed for display.

    Source markers are removed to reduce a known ISOT shortcut: truthful examples
    are predominantly Reuters stories while fake examples come from other outlets.
    """

    value = html.unescape(str(text or ""))
    value = CONTROL_PATTERN.sub(" ", value)
    value = URL_PATTERN.sub(" ", value)
    value = value.replace("\u00a0", " ")
    if remove_source_markers:
        value = REUTERS_LEAD.sub("", value)
        value = WIRE_MARKERS.sub("wire-service", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\s*\n\s*", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def text_for_model(text: str) -> str:
    """Return a conservative lower-case representation for TF-IDF modelling."""

    value = clean_article_text(text, remove_source_markers=True).lower()
    value = re.sub(r"\d+", " number ", value)
    value = re.sub(r"[^a-z\s'-]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def split_sentences(text: str) -> list[str]:
    """Split English prose into sentences without downloading NLTK resources."""

    cleaned = clean_article_text(text, remove_source_markers=False)
    if not cleaned:
        return []
    cleaned = re.sub(r"\s+", " ", cleaned)
    boundaries = re.compile(
        r"(?<=[.!?])\s+(?=(?:[\"'“‘(]?)[A-Z0-9])|(?<=;)\s+(?=[A-Z])"
    )
    parts = [part.strip() for part in boundaries.split(cleaned) if part.strip()]
    if len(parts) == 1 and len(cleaned) > 600:
        parts = [part.strip() for part in re.split(r"\n+", text) if part.strip()]
    return parts


def detect_language_hint(text: str) -> str:
    """Return a lightweight hint; it is intentionally not a language classifier."""

    letters = [char for char in text if char.isalpha()]
    if not letters:
        return "Unknown"
    latin = sum("a" <= char.lower() <= "z" for char in letters)
    return "English/Latin script" if latin / len(letters) >= 0.80 else "Non-English or mixed"
