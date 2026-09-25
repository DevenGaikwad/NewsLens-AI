"""Transparent consistency signals shared by offline benchmarking and runtime.

Every synthetic article contains two ordinary-language fact summaries: a
``Reference note`` and an ``Article account``.  Both labels use the same fields
and punctuation.  These helpers compare the values and append derived tokens
for a lightweight TF-IDF pipeline.  The derived tokens are not stored in the
dataset and are never presented as external fact-checking evidence.
"""

from __future__ import annotations

import hashlib
import html
import re
from collections.abc import Iterable


FACT_FIELDS = (
    "lead",
    "site",
    "date",
    "time",
    "quantity",
    "result",
    "attribution",
    "rationale",
    "status",
    "sequence",
    "certainty",
)

_BLOCK = re.compile(
    r"^(Reference note|Article account)\s*[—-]\s*(.+?)\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
_FIELD = re.compile(r"(?:^|;)\s*([a-z]+)\s*:\s*([^;]+)", flags=re.IGNORECASE)
_URL = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _canonical(value: str) -> str:
    value = html.unescape(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def fact_value_code(field: str, value: str) -> str:
    """Return a stable numeric code for one canonical fictional fact value.

    Numeric codes keep the reference/account comparison explicit while the
    model's normalizer maps every code to the same neutral ``number`` token.
    This prevents a raw bag-of-words model from learning whether an article
    repeats one human-readable value or mentions two different values.
    """

    canonical = _canonical(value)
    digest = hashlib.sha256(f"{field}:{canonical}".encode("utf-8")).digest()
    number = int.from_bytes(digest[:8], "big") % 10_000_000_000
    return f"{number:010d}"


def parse_fact_blocks(text: str) -> dict[str, dict[str, str]]:
    """Return canonical reference/account fields from one generated article."""

    parsed: dict[str, dict[str, str]] = {}
    for heading, body in _BLOCK.findall(str(text or "")):
        key = "reference" if heading.lower().startswith("reference") else "account"
        parsed[key] = {
            name.lower(): _canonical(value.rstrip(". "))
            for name, value in _FIELD.findall(body)
        }
    return parsed


def consistency_signal_tokens(text: str) -> list[str]:
    """Derive auditable match/mismatch tokens without consulting a label."""

    blocks = parse_fact_blocks(text)
    reference = blocks.get("reference", {})
    account = blocks.get("account", {})
    if not reference or not account:
        return ["signal_fact_blocks_unavailable"]

    tokens = ["signal_fact_blocks_present"]
    mismatches = 0
    available = 0
    for field in FACT_FIELDS:
        left = reference.get(field, "")
        right = account.get(field, "")
        if not left or not right:
            tokens.append(f"signal_{field}_unavailable")
            continue
        available += 1
        if left == right:
            tokens.append(f"signal_{field}_match")
        else:
            mismatches += 1
            tokens.append(f"signal_{field}_mismatch")
    tokens.append(f"signal_fields_available_{available}")
    tokens.append(f"signal_mismatch_count_{min(mismatches, 4)}")
    return tokens


def normalize_visible_text(text: str) -> str:
    """Apply deterministic model text normalization after signal extraction."""

    value = html.unescape(str(text or ""))
    value = _CONTROL.sub(" ", value)
    value = _URL.sub(" ", value)
    value = value.replace("\u00a0", " ").lower()
    value = re.sub(r"\d+", " number ", value)
    value = re.sub(r"[^a-z\s'_-]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def augment_text(text: str) -> str:
    """Return normalized article text plus transparent derived signal tokens."""

    normalized = normalize_visible_text(text)
    return f"{normalized} {' '.join(consistency_signal_tokens(text))}".strip()


def augment_texts(values: Iterable[object]) -> list[str]:
    """Batch form suitable for ``sklearn.preprocessing.FunctionTransformer``."""

    return [augment_text(str(value or "")) for value in values]
