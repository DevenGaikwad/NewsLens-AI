"""Small shared helpers with no Streamlit dependency."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


WORD_PATTERN = re.compile(r"\b[\w'-]+\b", flags=re.UNICODE)


def word_tokens(text: str) -> list[str]:
    """Return simple Unicode-aware word tokens."""

    return WORD_PATTERN.findall(text or "")


def word_count(text: str) -> int:
    """Count readable word-like tokens."""

    return len(word_tokens(text))


def reading_time_minutes(text: str, words_per_minute: int = 220) -> int:
    """Estimate reading time, rounded up to at least one minute."""

    count = word_count(text)
    return max(1, (count + words_per_minute - 1) // words_per_minute)


def article_hash(text: str) -> str:
    """Create a deterministic hash after whitespace/case normalisation."""

    normalised = " ".join((text or "").lower().split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def utc_now_iso() -> str:
    """Return a timezone-aware ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def domain_from_url(url: str | None) -> str:
    """Extract a lower-case hostname from a URL."""

    if not url:
        return ""
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def compression_ratio(original_words: int, summary_words: int) -> float:
    """Calculate percentage reduction in word count."""

    if original_words <= 0:
        return 0.0
    return round((1 - (summary_words / original_words)) * 100, 2)


def dump_json(path: Path, payload: Any) -> None:
    """Write UTF-8 JSON with stable, readable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    """Read JSON or return the supplied default when the file is absent."""

    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def safe_filename(value: str, fallback: str = "analysis") -> str:
    """Convert a title into a portable filename stem."""

    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value or "").strip("._")
    return (cleaned[:80] or fallback).lower()
