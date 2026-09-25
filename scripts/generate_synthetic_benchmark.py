"""Generate and audit the deterministic NewsLens synthetic benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from synthetic_benchmark.audit import (  # noqa: E402
    audit_dataset,
    select_manual_review_rows,
    write_json,
    write_manual_review_pack,
)
from synthetic_benchmark.generator import (  # noqa: E402
    DATASET_ID,
    FINAL_EVENT_COUNT,
    PILOT_EVENT_COUNT,
    RANDOM_SEED,
    articles_csv_bytes,
    build_dataset,
    events_jsonl_bytes,
    write_dataset_archive,
)


DEFAULT_ARCHIVE = ROOT / "data" / "synthetic" / f"{DATASET_ID}.zip"
DEFAULT_AUDIT = ROOT / "reports" / "synthetic_dataset_quality_audit.json"
DEFAULT_MANIFEST = ROOT / "data" / "synthetic" / "archive_manifest.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_pilot(output_dir: Path) -> dict[str, object]:
    rows, events = build_dataset(event_count=PILOT_EVENT_COUNT, seed=RANDOM_SEED)
    audit = audit_dataset(rows, events, expected_events=PILOT_EVENT_COUNT)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "articles.csv").write_bytes(articles_csv_bytes(rows))
    (output_dir / "events.jsonl").write_bytes(events_jsonl_bytes(events))
    write_json(output_dir / "quality_audit.json", audit)
    review_rows = select_manual_review_rows(rows, target_articles=200)
    write_manual_review_pack(output_dir / "manual_review_pack.md", review_rows)
    write_json(
        output_dir / "manual_review_sample.json",
        {
            "schema_version": 1,
            "dataset_id": DATASET_ID,
            "sample_articles": len(review_rows),
            "article_ids": [row["article_id"] for row in review_rows],
            "topics": sorted({row["topic"] for row in review_rows}),
            "labels": sorted({int(row["label"]) for row in review_rows}),
            "mutation_families": sorted(
                {
                    family
                    for row in review_rows
                    for family in str(row["mutation_family"]).split("+")
                }
            ),
        },
    )
    return {
        "mode": "pilot",
        "status": audit["status"],
        "event_count": len(events),
        "article_count": len(rows),
        "articles_sha256": hashlib.sha256(articles_csv_bytes(rows)).hexdigest(),
        "events_sha256": hashlib.sha256(events_jsonl_bytes(events)).hexdigest(),
        "manual_review_articles": len(review_rows),
        "output_directory": str(output_dir),
    }


def generate_final(archive_path: Path, audit_path: Path, manifest_path: Path) -> dict[str, object]:
    rows, events = build_dataset(event_count=FINAL_EVENT_COUNT, seed=RANDOM_SEED)
    audit = audit_dataset(rows, events, expected_events=FINAL_EVENT_COUNT)
    write_json(audit_path, audit)
    if audit["status"] != "passed":
        raise RuntimeError(f"Final dataset audit failed; inspect {audit_path}")
    archive = write_dataset_archive(archive_path, rows, events, audit)
    try:
        audit_reference = str(audit_path.relative_to(ROOT))
    except ValueError:
        audit_reference = audit_path.name
    manifest = {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "generator_version": "1.0.0",
        "seed": RANDOM_SEED,
        "regeneration_command": "python scripts/generate_synthetic_benchmark.py --mode final",
        "archive": archive,
        "audit_path": audit_reference,
    }
    write_json(manifest_path, manifest)
    return {
        "mode": "final",
        "status": "passed",
        "event_count": len(events),
        "article_count": len(rows),
        "archive": archive,
        "audit_path": str(audit_path),
        "manifest_path": str(manifest_path),
    }


def verify_archive(expected: Path) -> dict[str, object]:
    if not expected.is_file():
        raise FileNotFoundError(expected)
    with tempfile.TemporaryDirectory(prefix="newslens-synthetic-reproduction-") as directory:
        regenerated = Path(directory) / expected.name
        audit_path = Path(directory) / "quality_audit.json"
        manifest_path = Path(directory) / "archive_manifest.json"
        result = generate_final(regenerated, audit_path, manifest_path)
        expected_hash = _sha256(expected)
        regenerated_hash = _sha256(regenerated)
    if expected_hash != regenerated_hash:
        raise RuntimeError(
            f"Archive reproduction mismatch: expected {expected_hash}, regenerated {regenerated_hash}"
        )
    return {
        "mode": "verify",
        "status": "passed",
        "expected_archive": str(expected),
        "expected_sha256": expected_hash,
        "regenerated_sha256": regenerated_hash,
        "article_count": result["article_count"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pilot", "final", "verify"), required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "tmp" / "phase5s-pilot",
        help="Pilot output directory.",
    )
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "pilot":
        result = generate_pilot(args.output_dir.resolve())
    elif args.mode == "final":
        result = generate_final(args.archive.resolve(), args.audit.resolve(), args.manifest.resolve())
    else:
        result = verify_archive(args.archive.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
