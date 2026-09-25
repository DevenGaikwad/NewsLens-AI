"""Quality, leakage, and provenance audits for the synthetic benchmark."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .generator import (
    ARTICLE_COLUMNS,
    DATASET_ID,
    FINAL_EVENT_COUNT,
    GENERATOR_VERSION,
    MUTATION_FAMILIES,
    PENDING_RESULT,
    RANDOM_SEED,
    REVIEW_RESULT,
    SPLIT_COUNTS_PER_TOPIC,
    TOPICS,
)
from .signals import FACT_FIELDS, fact_value_code, normalize_visible_text, parse_fact_blocks


FORBIDDEN_VISIBLE_TERMS = (
    "fake",
    "false",
    "real",
    "reliable",
    "fabricated",
    "contradiction",
    "training",
    "validation",
    "calibration",
    "final test",
    "final-test",
    "split",
    "isot",
)
REAL_ENTITY_DENY_LIST = (
    "Reuters",
    "Associated Press",
    "BBC",
    "CNN",
    "Fox News",
    "The New York Times",
    "The Guardian",
    "OpenAI",
    "University of Victoria",
    "United Nations",
    "World Health Organization",
    "Donald Trump",
    "Joe Biden",
    "Narendra Modi",
    "Elon Musk",
)
NEAR_DUPLICATE_THRESHOLD = 0.82


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", str(text)))


def _normalized_content(row: dict[str, Any]) -> str:
    value = f"{row['title']}\n{row['text']}".casefold()
    return re.sub(r"\s+", " ", value).strip()


def _content_sha(row: dict[str, Any]) -> str:
    return hashlib.sha256(f"{row['title']}\n{row['text']}".encode("utf-8")).hexdigest()


def _shingles(text: str, width: int = 5) -> set[int]:
    tokens = re.findall(r"[a-z0-9]+", text.casefold())
    if len(tokens) < width:
        return set()
    return {
        int.from_bytes(
            hashlib.blake2b(" ".join(tokens[index : index + width]).encode("utf-8"), digest_size=8).digest(),
            "big",
        )
        for index in range(len(tokens) - width + 1)
    }


def _near_duplicate_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    signatures: list[tuple[int, ...]] = []
    event_members: dict[str, list[int]] = defaultdict(list)
    buckets: dict[tuple[int, tuple[int, ...]], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        event_members[str(row["event_id"])].append(index)
        values = sorted(_shingles(f"{row['title']} {row['text']}"))[:12]
        signature = tuple(values)
        signatures.append(signature)
        if len(signature) == 12:
            for band in range(3):
                buckets[(band, signature[band * 4 : (band + 1) * 4])].append(index)

    candidate_pairs: set[tuple[int, int]] = set()
    oversized_buckets = 0
    for members in buckets.values():
        if len(members) > 100:
            oversized_buckets += 1
            continue
        if len(members) > 1:
            candidate_pairs.update(combinations(sorted(members), 2))
    for members in event_members.values():
        if len(members) == 2:
            candidate_pairs.add(tuple(sorted(members)))

    cache: dict[int, set[int]] = {}
    findings: list[dict[str, Any]] = []
    max_similarity = 0.0
    max_pair: tuple[str, str] | None = None
    for left, right in sorted(candidate_pairs):
        left_set = cache.setdefault(left, _shingles(f"{rows[left]['title']} {rows[left]['text']}"))
        right_set = cache.setdefault(right, _shingles(f"{rows[right]['title']} {rows[right]['text']}"))
        if not left_set or not right_set:
            continue
        similarity = len(left_set & right_set) / len(left_set | right_set)
        if similarity > max_similarity:
            max_similarity = similarity
            max_pair = (str(rows[left]["article_id"]), str(rows[right]["article_id"]))
        if similarity >= NEAR_DUPLICATE_THRESHOLD:
            findings.append(
                {
                    "left_article_id": rows[left]["article_id"],
                    "right_article_id": rows[right]["article_id"],
                    "same_event": rows[left]["event_id"] == rows[right]["event_id"],
                    "similarity": round(float(similarity), 6),
                }
            )
    return {
        "method": (
            "Deterministic word-five-gram minimum-hash candidate screen with exact Jaccard "
            "verification; every within-event pair is also checked"
        ),
        "threshold": NEAR_DUPLICATE_THRESHOLD,
        "signature_bands": 3,
        "signature_values_per_band": 4,
        "oversized_common_template_buckets_skipped": oversized_buckets,
        "candidate_pairs_verified": len(candidate_pairs),
        "findings": findings,
        "finding_count": len(findings),
        "cross_event_finding_count": sum(not item["same_event"] for item in findings),
        "maximum_verified_similarity": round(float(max_similarity), 6),
        "maximum_pair_article_ids": list(max_pair) if max_pair else [],
        "limitation": (
            "Approximate candidate generation is not exhaustive semantic-duplicate detection; "
            "exact and normalized duplicate checks are exhaustive."
        ),
    }


def _distribution(frame: pd.DataFrame, fields: list[str]) -> dict[str, int]:
    counts = frame.groupby(fields, dropna=False).size()
    return {" | ".join(map(str, key if isinstance(key, tuple) else (key,))): int(value) for key, value in counts.items()}


def _metadata_predictability(frame: pd.DataFrame) -> dict[str, Any]:
    working = frame.copy()
    working["row_position_mod_2"] = np.arange(len(working)) % 2
    working["row_position_mod_5"] = np.arange(len(working)) % 5
    working["article_id_prefix"] = working["article_id"].str.replace("nlsa-", "", regex=False).str[0]
    working["event_id_prefix"] = working["event_id"].str.replace("nlse-", "", regex=False).str[0]
    working["word_count"] = working["text"].map(_word_count)
    working["paragraph_count"] = working["text"].str.count(r"\n\n") + 1
    working["title_word_count"] = working["title"].map(_word_count)
    working["punctuation_count"] = working["text"].str.count(r"[,:;.!?]")

    event_hash = working["event_id"].map(lambda value: int(hashlib.sha256(value.encode()).hexdigest()[:8], 16))
    train_mask = event_hash % 5 != 0
    eval_mask = ~train_mask
    categorical = [
        "topic",
        "template_family",
        "mutation_family",
        "split",
        "article_id_prefix",
        "event_id_prefix",
    ]
    numeric = [
        "word_count",
        "paragraph_count",
        "title_word_count",
        "punctuation_count",
        "row_position_mod_2",
        "row_position_mod_5",
    ]
    pipeline = Pipeline(
        [
            (
                "features",
                ColumnTransformer(
                    [
                        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
                        ("numeric", StandardScaler(), numeric),
                    ]
                ),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=800, random_state=RANDOM_SEED, solver="liblinear"),
            ),
        ]
    )
    pipeline.fit(working.loc[train_mask, categorical + numeric], working.loc[train_mask, "label"])
    predictions = pipeline.predict(working.loc[eval_mask, categorical + numeric])
    labels = working.loc[eval_mask, "label"]
    return {
        "features": categorical + numeric,
        "group_rule": "event hash modulo five; paired articles never cross fit/evaluation",
        "fit_rows": int(train_mask.sum()),
        "evaluation_rows": int(eval_mask.sum()),
        "accuracy": round(float(accuracy_score(labels, predictions)), 6),
        "balanced_accuracy": round(float(balanced_accuracy_score(labels, predictions)), 6),
        "pass_threshold": 0.58,
    }


def _raw_text_baseline(frame: pd.DataFrame) -> dict[str, Any]:
    event_hash = frame["event_id"].map(lambda value: int(hashlib.sha256(value.encode()).hexdigest()[:8], 16))
    train_mask = event_hash % 5 != 0
    eval_mask = ~train_mask
    text = (frame["title"] + "\n" + frame["text"]).astype(str).map(normalize_visible_text)
    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=3,
                    max_df=0.98,
                    max_features=12_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=800, random_state=RANDOM_SEED, solver="liblinear"),
            ),
        ]
    )
    pipeline.fit(text[train_mask], frame.loc[train_mask, "label"])
    predictions = pipeline.predict(text[eval_mask])
    labels = frame.loc[eval_mask, "label"]
    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["classifier"]
    names = np.asarray(vectorizer.get_feature_names_out())
    coefficients = classifier.coef_[0]

    def pack(indices: np.ndarray) -> list[dict[str, Any]]:
        return [
            {
                "term": str(names[index]),
                "coefficient": round(float(coefficients[index]), 6),
            }
            for index in indices
        ]

    return {
        "purpose": "Detect surface-style leakage before derived consistency signals are added",
        "group_rule": "event hash modulo five; paired articles never cross fit/evaluation",
        "fit_rows": int(train_mask.sum()),
        "evaluation_rows": int(eval_mask.sum()),
        "accuracy": round(float(accuracy_score(labels, predictions)), 6),
        "balanced_accuracy": round(float(balanced_accuracy_score(labels, predictions)), 6),
        "material_leakage_threshold": 0.75,
        "strongest_consistent_coefficients": pack(np.argsort(coefficients)[-25:][::-1]),
        "strongest_contradicting_coefficients": pack(np.argsort(coefficients)[:25]),
    }


def _top_ngrams(frame: pd.DataFrame) -> dict[str, Any]:
    text = (frame["title"] + "\n" + frame["text"]).astype(str)
    vectorizer = CountVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=3,
        max_features=12_000,
        binary=True,
    )
    matrix = vectorizer.fit_transform(text)
    names = np.asarray(vectorizer.get_feature_names_out())
    label0 = np.asarray(matrix[frame["label"].to_numpy() == 0].mean(axis=0)).ravel()
    label1 = np.asarray(matrix[frame["label"].to_numpy() == 1].mean(axis=0)).ravel()
    delta = label1 - label0
    label0_counts = np.asarray(matrix[frame["label"].to_numpy() == 0].sum(axis=0)).ravel()
    label1_counts = np.asarray(matrix[frame["label"].to_numpy() == 1].sum(axis=0)).ravel()

    def pack(indices: np.ndarray) -> list[dict[str, Any]]:
        return [
            {
                "term": str(names[index]),
                "ledger_consistent_document_rate": round(float(label1[index]), 6),
                "ledger_contradicting_document_rate": round(float(label0[index]), 6),
                "rate_delta": round(float(delta[index]), 6),
            }
            for index in indices
        ]

    exclusive_indices = np.flatnonzero((label0_counts == 0) | (label1_counts == 0))
    exclusive = sorted(
        (
            {
                "term": str(names[index]),
                "ledger_consistent_documents": int(label1_counts[index]),
                "ledger_contradicting_documents": int(label0_counts[index]),
            }
            for index in exclusive_indices
        ),
        key=lambda finding: max(
            finding["ledger_consistent_documents"],
            finding["ledger_contradicting_documents"],
        ),
        reverse=True,
    )
    return {
        "largest_consistent_deltas": pack(np.argsort(delta)[-25:][::-1]),
        "largest_contradicting_deltas": pack(np.argsort(delta)[:25]),
        "maximum_absolute_document_rate_delta": round(float(np.max(np.abs(delta))), 6),
        "label_exclusive_term_count": len(exclusive),
        "largest_label_exclusive_terms": exclusive[:25],
    }


def _account_value_marginals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        field: {0: Counter(), 1: Counter()}
        for field in FACT_FIELDS
    }
    for row in rows:
        account = parse_fact_blocks(str(row["text"])).get("account", {})
        label = int(row["label"])
        for field in FACT_FIELDS:
            counts[field][label][account.get(field, "")] += 1

    fields: dict[str, Any] = {}
    exact = True
    for field, by_label in counts.items():
        keys = set(by_label[0]) | set(by_label[1])
        total0 = sum(by_label[0].values())
        total1 = sum(by_label[1].values())
        maximum_count_delta = max(
            (abs(by_label[0][key] - by_label[1][key]) for key in keys),
            default=0,
        )
        total_variation = sum(
            abs(by_label[0][key] / total0 - by_label[1][key] / total1)
            for key in keys
        ) / 2
        field_exact = by_label[0] == by_label[1]
        exact = exact and field_exact
        fields[field] = {
            "exact": field_exact,
            "value_count": len(keys),
            "maximum_count_delta": maximum_count_delta,
            "total_variation": round(float(total_variation), 6),
            "ledger_consistent_exclusive_value_count": sum(
                by_label[1][key] > 0 and by_label[0][key] == 0 for key in keys
            ),
            "ledger_contradicting_exclusive_value_count": sum(
                by_label[0][key] > 0 and by_label[1][key] == 0 for key in keys
            ),
        }
    return {
        "exact_across_all_fields": exact,
        "fields": fields,
    }


def _fact_code_collisions(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen: dict[str, dict[str, str]] = {
        field: {} for field in FACT_FIELDS
    }
    findings: list[dict[str, str]] = []
    for event in events:
        for record_name in ("ledger", "contradicted_account"):
            record = event[record_name]
            for field in FACT_FIELDS:
                value = str(record[field])
                code = fact_value_code(field, value)
                previous = seen[field].setdefault(code, value)
                if previous != value:
                    findings.append(
                        {
                            "field": field,
                            "code": code,
                            "first_value": previous,
                            "second_value": value,
                        }
                    )
    return findings


def select_manual_review_rows(rows: list[dict[str, Any]], target_articles: int = 200) -> list[dict[str, Any]]:
    if target_articles % 2:
        raise ValueError("Manual review target must contain complete event pairs.")
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_event[str(row["event_id"])].append(row)
    target_events = target_articles // 2
    topic_targets = {topic.slug: target_events // len(TOPICS) for topic in TOPICS}
    for topic in TOPICS[: target_events % len(TOPICS)]:
        topic_targets[topic.slug] += 1

    selected: list[str] = []
    for topic in TOPICS:
        candidates = [
            event_id
            for event_id, pair in by_event.items()
            if pair[0]["topic"] == topic.slug
        ]
        candidates.sort(
            key=lambda event_id: (
                MUTATION_FAMILIES.index(by_event[event_id][0]["mutation_family"].split("+")[0]),
                hashlib.sha256(event_id.encode()).hexdigest(),
            )
        )
        needed = topic_targets[topic.slug]
        covered: set[str] = set()
        topic_selected: list[str] = []
        for event_id in candidates:
            primary = by_event[event_id][0]["mutation_family"].split("+")[0]
            if primary not in covered:
                topic_selected.append(event_id)
                covered.add(primary)
            if len(topic_selected) == needed:
                break
        if len(topic_selected) < needed:
            topic_selected.extend(
                event_id for event_id in candidates if event_id not in topic_selected
            )
        selected.extend(topic_selected[:needed])

    review_rows = [row for event_id in selected for row in by_event[event_id]]
    return sorted(review_rows, key=lambda row: (str(row["topic"]), str(row["event_id"]), -int(row["label"])))


def write_manual_review_pack(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = [
        "# Phase 5S Synthetic Pilot Manual Review Pack",
        "",
        "Review every article for grammar, coherence, fictional scope, meaningful fact comparison, neutral tone, and absence of visible label cues.",
        "",
    ]
    for index, row in enumerate(rows, start=1):
        sections.extend(
            [
                f"## {index:03d} {row['article_id']}",
                "",
                f"- Event: `{row['event_id']}`",
                f"- Topic: `{row['topic']}`",
                f"- Label: `{row['label_name']}`",
                f"- Template: `{row['template_family']}`",
                f"- Mutation plan: `{row['mutation_family']}`",
                "",
                f"### {row['title']}",
                "",
                str(row["text"]),
                "",
                "---",
                "",
            ]
        )
    path.write_text("\n".join(sections), encoding="utf-8", newline="\n")


def audit_dataset(
    rows: list[dict[str, Any]],
    events: list[dict[str, Any]],
    *,
    expected_events: int,
) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    expected_columns = set(ARTICLE_COLUMNS)
    missing_columns = sorted(expected_columns - set(frame.columns))
    extra_columns = sorted(set(frame.columns) - expected_columns)
    missing_values = {column: int(frame[column].isna().sum()) for column in frame.columns}
    missing_values = {column: count for column, count in missing_values.items() if count}
    invalid_labels = int((~frame["label"].isin([0, 1])).sum())
    invalid_label_names = int(
        (
            ~frame.apply(
                lambda row: row["label_name"]
                == ("synthetic_ledger_consistent" if row["label"] == 1 else "synthetic_ledger_contradicting"),
                axis=1,
            )
        ).sum()
    )

    exact_values = [f"{row['title']}\n{row['text']}" for row in rows]
    normalized_values = [_normalized_content(row) for row in rows]
    exact_duplicates = len(exact_values) - len(set(exact_values))
    normalized_duplicates = len(normalized_values) - len(set(normalized_values))
    content_hash_duplicates = len(frame) - frame["content_sha256"].nunique()
    invalid_hashes = sum(row["content_sha256"] != _content_sha(row) for row in rows)

    pair_violations: list[str] = []
    event_split_overlap = 0
    event_groups = frame.groupby("event_id")
    for event_id, group in event_groups:
        if len(group) != 2 or set(group["label"]) != {0, 1}:
            pair_violations.append(str(event_id))
        if group["split"].nunique() != 1:
            event_split_overlap += 1

    hashes_by_split = frame.groupby("split")["content_sha256"].apply(set)
    content_cross_split_overlap = 0
    split_names = sorted(hashes_by_split.index)
    for left_index, left in enumerate(split_names):
        for right in split_names[left_index + 1 :]:
            content_cross_split_overlap += len(hashes_by_split[left] & hashes_by_split[right])

    word_counts = frame["text"].map(_word_count)
    out_of_range = int(((word_counts < 180) | (word_counts > 550)).sum())
    visible_text = (frame["title"] + "\n" + frame["text"]).astype(str)
    forbidden_findings: list[dict[str, str]] = []
    for term in FORBIDDEN_VISIBLE_TERMS:
        pattern = re.compile(rf"\b{re.escape(term)}\b", flags=re.IGNORECASE)
        matches = frame.loc[visible_text.str.contains(pattern, regex=True), "article_id"].tolist()
        forbidden_findings.extend({"article_id": str(value), "term": term} for value in matches[:20])
    deny_findings: list[dict[str, str]] = []
    for term in REAL_ENTITY_DENY_LIST:
        pattern = re.compile(rf"\b{re.escape(term)}\b", flags=re.IGNORECASE)
        matches = frame.loc[visible_text.str.contains(pattern, regex=True), "article_id"].tolist()
        deny_findings.extend({"article_id": str(value), "term": term} for value in matches[:20])

    fact_violations: list[dict[str, Any]] = []
    coherence_violations: list[dict[str, Any]] = []
    topic_specs = {topic.slug: topic for topic in TOPICS}
    events_by_id = {str(event["event_id"]): event for event in events}
    mismatch_counts: Counter[int] = Counter()
    for row in rows:
        blocks = parse_fact_blocks(str(row["text"]))
        reference = blocks.get("reference", {})
        account = blocks.get("account", {})
        event = events_by_id.get(str(row["event_id"]), {})
        ledger = event.get("ledger", {})
        expected_account = (
            ledger
            if int(row["label"]) == 1
            else event.get("contradicted_account", {})
        )
        expected_reference_codes = {
            field: fact_value_code(field, str(ledger.get(field, "")))
            for field in FACT_FIELDS
        }
        expected_account_codes = {
            field: fact_value_code(field, str(expected_account.get(field, "")))
            for field in FACT_FIELDS
        }
        mismatch_fields = {
            field for field in FACT_FIELDS if reference.get(field) != account.get(field)
        }
        mismatches = len(mismatch_fields)
        mismatch_counts[mismatches] += 1
        families = set(str(row["mutation_family"]).split("+"))
        expected_fields = {
            field
            for family, field in {
                "entity_substitution": "lead",
                "location_contradiction": "site",
                "quantity_change": "quantity",
                "result_reversal": "result",
                "attribution_change": "attribution",
                "causal_fabrication": "rationale",
                "policy_status_inversion": "status",
                "sequence_reversal": "sequence",
                "unsupported_certainty": "certainty",
            }.items()
            if family in families
        }
        if "date_time_displacement" in families:
            expected_fields.add("date" if reference.get("date") != account.get("date") else "time")
        if "policy_status_inversion" in families:
            # The generator deliberately couples the outcome to a changed
            # status so each fictional account remains internally coherent.
            expected_fields.add("result")
        if "result_reversal" in families:
            # Outcome reversal likewise moves the account to a compatible
            # status rather than leaving impossible temporal combinations.
            expected_fields.add("status")
        if int(row["label"]) == 1:
            expected_fields.clear()
        valid = (
            set(reference) == set(FACT_FIELDS)
            and set(account) == set(FACT_FIELDS)
            and reference == expected_reference_codes
            and account == expected_account_codes
            and mismatch_fields == expected_fields
        )
        if not valid:
            fact_violations.append(
                {
                    "article_id": row["article_id"],
                    "label": int(row["label"]),
                    "planned_mutations": len(families),
                    "observed_mismatches": mismatches,
                    "expected_fields": sorted(expected_fields),
                    "observed_fields": sorted(mismatch_fields),
                }
            )
        spec = topic_specs[str(row["topic"])]
        status = expected_account.get("status")
        result = expected_account.get("result")
        coherent = (
            (status in {"approved", "fully authorised", "completed"} and result in spec.results)
            or (status in {"withdrawn", "cancelled", "not started"} and result in spec.reverse_results)
            or (status == "scheduled" and result == PENDING_RESULT)
            or (status == "under review" and result == REVIEW_RESULT)
        )
        if set(account) == set(FACT_FIELDS) and not coherent:
            coherence_violations.append(
                {
                    "article_id": row["article_id"],
                    "status": status,
                    "result": result,
                }
            )

    label_counts = {str(key): int(value) for key, value in frame["label"].value_counts().sort_index().items()}
    split_counts = {str(key): int(value) for key, value in frame["split"].value_counts().sort_index().items()}
    expected_final_splits = {
        name: count * len(TOPICS) * 2 for name, count in SPLIT_COUNTS_PER_TOPIC.items()
    }
    split_contract_passed = expected_events != FINAL_EVENT_COUNT or split_counts == expected_final_splits

    metadata = _metadata_predictability(frame)
    raw_text = _raw_text_baseline(frame)
    near_duplicates = _near_duplicate_audit(rows)
    ngrams = _top_ngrams(frame)
    account_marginals = _account_value_marginals(rows)
    fact_code_collisions = _fact_code_collisions(events)

    checks = {
        "schema": not missing_columns and not extra_columns,
        "row_count": len(rows) == expected_events * 2 and len(events) == expected_events,
        "balanced_labels": label_counts == {"0": expected_events, "1": expected_events},
        "split_contract": split_contract_passed,
        "missing_values": not missing_values,
        "valid_labels": invalid_labels == 0 and invalid_label_names == 0,
        "exact_duplicates": exact_duplicates == 0,
        "normalized_duplicates": normalized_duplicates == 0,
        "content_hashes": content_hash_duplicates == 0 and invalid_hashes == 0,
        "paired_events": not pair_violations,
        "cross_split_events": event_split_overlap == 0,
        "cross_split_content": content_cross_split_overlap == 0,
        "article_length": out_of_range == 0,
        "forbidden_visible_terms": not forbidden_findings,
        "real_entity_deny_list": not deny_findings,
        "fact_comparison": not fact_violations,
        "status_result_coherence": not coherence_violations,
        "near_duplicates": near_duplicates["finding_count"] == 0,
        "metadata_predictability": metadata["balanced_accuracy"] <= metadata["pass_threshold"],
        "surface_style_leakage": raw_text["balanced_accuracy"] <= raw_text["material_leakage_threshold"],
        "account_value_pool_symmetry": (
            expected_events != FINAL_EVENT_COUNT
            or account_marginals["exact_across_all_fields"]
        ),
        "fact_code_uniqueness": not fact_code_collisions,
    }
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "generator_version": GENERATOR_VERSION,
        "seed": RANDOM_SEED,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "article_count": len(rows),
        "event_count": len(events),
        "schema": {
            "required_columns": list(ARTICLE_COLUMNS),
            "missing_columns": missing_columns,
            "extra_columns": extra_columns,
        },
        "label_counts": label_counts,
        "split_counts": split_counts,
        "expected_final_split_counts": expected_final_splits if expected_events == FINAL_EVENT_COUNT else None,
        "topic_by_label_and_split": _distribution(frame, ["topic", "label", "split"]),
        "template_by_label_and_split": _distribution(frame, ["template_family", "label", "split"]),
        "mutation_plan_by_label": _distribution(frame, ["mutation_family", "label"]),
        "primary_mutation_distribution": dict(
            sorted(Counter(value.split("+")[0] for value in frame.loc[frame["label"] == 0, "mutation_family"]).items())
        ),
        "word_count": {
            "minimum": int(word_counts.min()),
            "maximum": int(word_counts.max()),
            "mean": round(float(word_counts.mean()), 3),
            "median": round(float(word_counts.median()), 3),
            "by_label": {
                str(label): {
                    "minimum": int(word_counts[frame["label"] == label].min()),
                    "maximum": int(word_counts[frame["label"] == label].max()),
                    "mean": round(float(word_counts[frame["label"] == label].mean()), 3),
                }
                for label in (0, 1)
            },
        },
        "missing_values": missing_values,
        "invalid_label_count": invalid_labels,
        "invalid_label_name_count": invalid_label_names,
        "exact_duplicate_count": exact_duplicates,
        "normalized_duplicate_count": normalized_duplicates,
        "content_hash_duplicate_count": content_hash_duplicates,
        "invalid_content_hash_count": invalid_hashes,
        "event_pair_violation_count": len(pair_violations),
        "cross_split_event_overlap": event_split_overlap,
        "cross_split_content_hash_overlap": content_cross_split_overlap,
        "out_of_range_article_count": out_of_range,
        "forbidden_term_findings": forbidden_findings,
        "real_entity_deny_list_findings": deny_findings,
        "fact_comparison_violation_count": len(fact_violations),
        "status_result_coherence_violation_count": len(coherence_violations),
        "mismatch_count_distribution": {str(key): int(value) for key, value in sorted(mismatch_counts.items())},
        "near_duplicate_detection": near_duplicates,
        "metadata_only_predictability": metadata,
        "raw_text_surface_baseline": raw_text,
        "top_unigrams_and_bigrams_by_label": ngrams,
        "account_value_marginal_symmetry": account_marginals,
        "fact_code_collision_findings": fact_code_collisions,
        "limitations": [
            "The real-entity deny-list is a targeted safeguard, not proof that no fictional token resembles any real name.",
            "Near-duplicate candidate generation is approximate; exact and normalized duplicate checks are exhaustive.",
            "Metadata and surface-style baselines detect major leakage but cannot prove that every possible shortcut is absent.",
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
