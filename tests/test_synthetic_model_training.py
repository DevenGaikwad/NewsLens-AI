"""Lightweight contracts for the accepted archive and public model package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import pandas as pd

from synthetic_benchmark.signals import consistency_signal_tokens


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/synthetic/newslens-synthetic-articles-v1.0.0.zip"


def _json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_authoritative_archive_identity() -> None:
    assert ARCHIVE.stat().st_size == 10_319_934
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == "3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc"
    payload = ARCHIVE.read_bytes()
    assert hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest() == "cb0d5e57407be10fecefb34762e586bacd38dd56"


def test_authored_splits_are_group_safe() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        frame = pd.read_csv(archive.open("articles.csv"))
    assert frame["split"].value_counts().to_dict() == {
        "training": 18_000,
        "model_validation": 2_400,
        "calibration": 1_200,
        "abstention_policy": 1_200,
        "final_test": 1_200,
    }
    assert frame.groupby("event_id")["split"].nunique().max() == 1
    assert frame.groupby("content_sha256")["split"].nunique().max() == 1


def test_signal_extraction_depends_on_visible_fields() -> None:
    consistent = "Reference note - lead: 10; site: 20.\nArticle account - lead: 10; site: 20."
    contradicting = "Reference note - lead: 10; site: 20.\nArticle account - lead: 10; site: 99."
    assert "signal_site_match" in consistency_signal_tokens(consistent)
    assert "signal_site_mismatch" in consistency_signal_tokens(contradicting)


def test_public_calibration_is_bound_to_exact_model() -> None:
    manifest = _json("models/public_artifact_manifest.json")
    calibration = _json("models/newslens_synthetic_calibration.json")
    model_path = ROOT / manifest["artifacts"]["model"]["path"]
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    assert model_hash == manifest["artifacts"]["model"]["sha256"]
    assert model_hash == calibration["model_sha256"]
    assert manifest["synthetic_only"] is True


def test_locked_metrics_and_shortcut_controls_are_recorded() -> None:
    summary = _json("reports/model_benchmark_summary.json")
    metrics = summary["locked_final_test"]["metrics"]
    assert summary["locked_final_test"]["evaluated_once"] is True
    assert metrics["balanced_accuracy"] == 1.0
    assert metrics["confusion_matrix"] == [[600, 0], [0, 600]]
    assert summary["shortcut_resistance"]["surface_text_only"]["balanced_accuracy"] <= 0.55
    assert summary["shortcut_resistance"]["metadata_only"]["balanced_accuracy"] <= 0.55
    assert summary["counterfactual_evaluation"]["prediction_flip_rate"] == 1.0
