"""Experimental, label-independent relational features for Phase 5X.

The authored reference and article-account strings are compared by field.
Only unambiguous zero-to-ninety-nine quantity words are made equivalent to
digits; other text remains a literal canonical comparison. The runtime guard
continues to govern incomplete or ambiguous fields.
"""

from __future__ import annotations

from collections.abc import Iterable

from .signals import FACT_FIELDS, normalize_visible_text, parse_fact_blocks


_UNITS = {name: number for number, name in enumerate((
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
    "eighteen", "nineteen",
))}
_TENS = {name: number for number, name in (
    (20, "twenty"), (30, "thirty"), (40, "forty"), (50, "fifty"),
    (60, "sixty"), (70, "seventy"), (80, "eighty"), (90, "ninety"),
)}


def _quantity(value: str) -> str:
    parts = value.replace("-", " ").split()
    if value.isdecimal() and len(value) <= 2:
        return str(int(value))
    if len(parts) == 1:
        number = _UNITS.get(parts[0], _TENS.get(parts[0]))
    elif len(parts) == 2 and parts[0] in _TENS and parts[1] in _UNITS and _UNITS[parts[1]] < 10:
        number = _TENS[parts[0]] + _UNITS[parts[1]]
    else:
        number = None
    return str(number) if number is not None else value


def relational_tokens(text: str) -> list[str]:
    blocks = parse_fact_blocks(text)
    reference, account = blocks.get("reference", {}), blocks.get("account", {})
    if not reference or not account:
        return ["rel_blocks_unavailable"]
    tokens = ["rel_blocks_present"]
    mismatches = 0
    available = 0
    for field in FACT_FIELDS:
        left, right = reference.get(field, ""), account.get(field, "")
        if not left or not right:
            tokens.append(f"rel_{field}_unavailable")
            continue
        available += 1
        if field == "quantity":
            left, right = _quantity(left), _quantity(right)
        if left == right:
            tokens.append(f"rel_{field}_match")
        else:
            mismatches += 1
            tokens.append(f"rel_{field}_mismatch")
    tokens.append("rel_any_mismatch" if mismatches else "rel_no_mismatch")
    tokens.append(f"rel_available_{available}")
    return tokens


def augment_relational_texts(values: Iterable[object]) -> list[str]:
    return [f"{normalize_visible_text(str(value or ''))} {' '.join(relational_tokens(str(value or '')))}".strip() for value in values]
