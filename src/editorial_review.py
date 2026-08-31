"""Validation helpers for the session-local human editorial review workflow."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit

from .text_preprocessor import CONTROL_PATTERN


REVIEW_STATUSES = (
    "Pending review",
    "Evidence supports the claim",
    "Evidence contradicts the claim",
    "Inconclusive",
    "Out of supported scope",
)
MAX_REVIEW_NOTES_CHARS = 4_000
MAX_ASSESSMENT_CHARS = 2_000
MAX_SUPPORTING_URLS = 8


def _clean_text(value: object, limit: int) -> str:
    cleaned = CONTROL_PATTERN.sub(" ", str(value or "")).strip()
    if len(cleaned) > limit:
        raise ValueError(f"Review text must not exceed {limit:,} characters.")
    return cleaned


def _validate_public_http_url(value: str) -> str:
    if len(value) > 2048:
        raise ValueError("A supporting-source URL is too long.")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Supporting sources must use a complete public HTTP(S) URL.")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Local supporting-source URLs are not accepted.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address and (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        raise ValueError("Private-network supporting-source URLs are not accepted.")
    return value


def normalise_supporting_urls(value: object) -> tuple[str, ...]:
    candidates = [line.strip() for line in str(value or "").splitlines() if line.strip()]
    if len(candidates) > MAX_SUPPORTING_URLS:
        raise ValueError(f"Add no more than {MAX_SUPPORTING_URLS} supporting-source URLs.")
    unique: list[str] = []
    for candidate in candidates:
        validated = _validate_public_http_url(candidate)
        if validated not in unique:
            unique.append(validated)
    return tuple(unique)


def validate_review_update(
    *,
    review_status: str,
    reviewer_notes: object,
    supporting_source_urls: object,
    final_editorial_assessment: object,
) -> dict[str, str]:
    if review_status not in REVIEW_STATUSES:
        raise ValueError("Choose one of the supported editorial-review statuses.")
    urls = normalise_supporting_urls(supporting_source_urls)
    return {
        "review_status": review_status,
        "reviewer_notes": _clean_text(reviewer_notes, MAX_REVIEW_NOTES_CHARS),
        "supporting_source_urls": "\n".join(urls),
        "final_editorial_assessment": _clean_text(
            final_editorial_assessment, MAX_ASSESSMENT_CHARS
        ),
    }
