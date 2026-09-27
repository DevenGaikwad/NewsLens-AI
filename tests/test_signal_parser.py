"""Regression cases for linear parsing of the authored fact summaries."""

from __future__ import annotations

from synthetic_benchmark.signals import (
    augment_text,
    consistency_signal_tokens,
    parse_fact_blocks,
)


def test_agreement_and_conflict_use_visible_field_values() -> None:
    reference = "Reference note - lead: 10; site: 20.\n"
    agree = reference + "Article account - lead: 10; site: 20."
    conflict = reference + "Article account - lead: 10; site: 99."

    assert parse_fact_blocks(agree)["reference"] == {"lead": "10", "site": "20"}
    assert "signal_site_match" in consistency_signal_tokens(agree)
    assert "signal_site_mismatch" in consistency_signal_tokens(conflict)
    assert augment_text(agree).endswith("signal_mismatch_count_0")


def test_crlf_whitespace_and_colons_inside_values() -> None:
    article = (
        "Reference note  —  lead :  A:B:C ; site: west:hall.\r\n"
        "Article account - lead: A:B:C; site: west:hall."
    )

    assert parse_fact_blocks(article) == {
        "reference": {"lead": "a b c", "site": "west hall"},
        "account": {"lead": "a b c", "site": "west hall"},
    }


def test_malformed_names_and_missing_fields_are_not_invented() -> None:
    article = (
        "Reference note - lead-: invalid; 9site: invalid; site: east.\n"
        "Article account - lead: sample."
    )

    assert parse_fact_blocks(article) == {
        "reference": {"site": "east"},
        "account": {"lead": "sample"},
    }
    assert "signal_site_unavailable" in consistency_signal_tokens(article)


def test_later_duplicate_fields_and_blocks_replace_earlier_values() -> None:
    article = (
        "Reference note - lead: old; lead: NEW; site: east.\n"
        "Reference note - lead: final; site: west.\n"
        "Article account - lead: final; site: west."
    )

    assert parse_fact_blocks(article)["reference"] == {"lead": "final", "site": "west"}
    assert "signal_lead_match" in consistency_signal_tokens(article)


def test_empty_or_malformed_blocks_do_not_consume_following_lines() -> None:
    article = "Reference note -\nArticle account - lead: 10."

    assert parse_fact_blocks(article) == {"account": {"lead": "10"}}
    assert consistency_signal_tokens(article) == ["signal_fact_blocks_unavailable"]


def test_long_malformed_input_has_no_partial_fact_match() -> None:
    article = "Reference note - " + ("lead " * 20_000) + ": value without semicolon"

    assert parse_fact_blocks(article) == {"reference": {}}
    assert consistency_signal_tokens(article) == ["signal_fact_blocks_unavailable"]
