from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

from synthetic_benchmark.generator import (
    ARTICLE_COLUMNS,
    FINAL_EVENT_COUNT,
    MUTATION_FAMILIES,
    RANDOM_SEED,
    TOPICS,
    _event_ledger,
    _mutate_ledger,
    _mutation_plan,
    articles_csv_bytes,
    build_dataset,
    events_jsonl_bytes,
    write_dataset_archive,
)
from synthetic_benchmark.signals import FACT_FIELDS, fact_value_code


def test_small_generation_is_byte_deterministic() -> None:
    first_rows, first_events = build_dataset(event_count=48, seed=RANDOM_SEED)
    second_rows, second_events = build_dataset(event_count=48, seed=RANDOM_SEED)

    assert articles_csv_bytes(first_rows) == articles_csv_bytes(second_rows)
    assert events_jsonl_bytes(first_events) == events_jsonl_bytes(second_events)
    assert len(first_rows) == 96
    assert len(first_events) == 48
    assert set(first_rows[0]) == set(ARTICLE_COLUMNS)
    assert Counter(row["label"] for row in first_rows) == {0: 48, 1: 48}
    assert all(len(pair) == 2 for pair in _rows_by_event(first_rows).values())


def test_full_release_count_and_split_contract() -> None:
    rows, events = build_dataset(event_count=FINAL_EVENT_COUNT, seed=RANDOM_SEED)

    assert len(events) == 12_000
    assert len(rows) == 24_000
    assert Counter(row["label"] for row in rows) == {0: 12_000, 1: 12_000}
    assert Counter(row["split"] for row in rows) == {
        "training": 18_000,
        "model_validation": 2_400,
        "calibration": 1_200,
        "abstention_policy": 1_200,
        "final_test": 1_200,
    }
    assert all(
        len(pair) == 2
        and {row["label"] for row in pair} == {0, 1}
        and len({row["split"] for row in pair}) == 1
        for pair in _rows_by_event(rows).values()
    )


def test_mutated_value_pools_are_label_symmetric() -> None:
    fields = (
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
    values = {field: {0: Counter(), 1: Counter()} for field in fields}
    fact_codes = {field: {} for field in FACT_FIELDS}
    plan_counts: Counter[tuple[str, ...]] = Counter()
    primary_counts: Counter[str] = Counter()

    for topic_index, spec in enumerate(TOPICS):
        for local_index in range(1_000):
            global_index = topic_index * 1_000 + local_index
            families = _mutation_plan(global_index)
            ledger = _event_ledger(spec, global_index, local_index, RANDOM_SEED)
            account = _mutate_ledger(
                ledger,
                spec,
                global_index,
                families,
                RANDOM_SEED,
            )
            plan_counts[families] += 1
            primary_counts[families[0]] += 1
            for field in fields:
                values[field][1][ledger[field]] += 1
                values[field][0][account[field]] += 1
                for value in (ledger[field], account[field]):
                    code = fact_value_code(field, value)
                    assert fact_codes[field].setdefault(code, value) == value

            changed = {field for field in fields if ledger[field] != account[field]}
            assert 2 <= len(families) <= 4
            assert changed
            assert all(_family_changed(family, ledger, account) for family in families)

    assert len(plan_counts) == 30
    assert set(plan_counts.values()) == {400}
    assert primary_counts == Counter({family: 1_200 for family in MUTATION_FAMILIES})
    assert all(by_label[0] == by_label[1] for by_label in values.values())


def test_archive_writer_is_byte_deterministic(tmp_path: Path) -> None:
    rows, events = build_dataset(event_count=48, seed=RANDOM_SEED)
    audit = {
        "article_count": len(rows),
        "event_count": len(events),
        "split_counts": dict(Counter(row["split"] for row in rows)),
        "raw_text_surface_baseline": {"balanced_accuracy": 0.5},
        "metadata_only_predictability": {"balanced_accuracy": 0.5},
    }
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    write_dataset_archive(first, rows, events, audit)
    write_dataset_archive(second, rows, events, audit)

    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == [
            "DATASET_CARD.md",
            "LICENSE.txt",
            "articles.csv",
            "checksums.sha256",
            "events.jsonl",
            "manifest.json",
            "provenance.json",
            "quality_audit.json",
        ]
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist())


def test_committed_archive_matches_manifests_and_audit() -> None:
    root = Path(__file__).resolve().parents[1]
    archive_path = root / "data" / "synthetic" / "newslens-synthetic-articles-v1.0.0.zip"
    outer_manifest = json.loads(
        (root / "data" / "synthetic" / "archive_manifest.json").read_text(encoding="utf-8")
    )
    audit = json.loads(
        (root / "reports" / "synthetic_dataset_quality_audit.json").read_text(encoding="utf-8")
    )

    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == outer_manifest["archive"]["sha256"]
    assert archive_path.stat().st_size == outer_manifest["archive"]["size_bytes"]
    assert audit["status"] == "passed"
    assert all(audit["checks"].values())
    assert audit["raw_text_surface_baseline"]["balanced_accuracy"] <= 0.75
    assert audit["article_count"] == 24_000
    assert audit["event_count"] == 12_000

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert names == outer_manifest["archive"]["entries"]
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist())
        assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names)
        checksum_entries = {
            line.split("  ", 1)[1]: line.split("  ", 1)[0]
            for line in archive.read("checksums.sha256").decode("utf-8").splitlines()
        }
        assert all(
            hashlib.sha256(archive.read(name)).hexdigest() == digest
            for name, digest in checksum_entries.items()
        )


def _rows_by_event(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["event_id"]), []).append(row)
    return grouped


def _family_changed(
    family: str,
    ledger: dict[str, str],
    account: dict[str, str],
) -> bool:
    if family == "date_time_displacement":
        return ledger["date"] != account["date"] or ledger["time"] != account["time"]
    field = {
        "entity_substitution": "lead",
        "location_contradiction": "site",
        "quantity_change": "quantity",
        "result_reversal": "result",
        "attribution_change": "attribution",
        "causal_fabrication": "rationale",
        "policy_status_inversion": "status",
        "sequence_reversal": "sequence",
        "unsupported_certainty": "certainty",
    }[family]
    return ledger[field] != account[field]
