"""Ownership, artifact-integrity, and public-release security contracts."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import shutil
import sys

from scripts import audit_public_release as release_audit


ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Deven Sachin Gaikwad"
COPYRIGHT = "© 2026 Deven Sachin Gaikwad. All Rights Reserved."


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _write(root: Path, relative: str, content: str = "") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _minimal_release_tree(root: Path) -> None:
    (root / ".git").mkdir()
    _write(root, "app.py")
    _write(root, ".gitignore", "models/fake_news_pipeline.joblib\nmodels/confidence_calibration.json\n")
    _write(root, ".gitattributes")
    _write(root, "LICENSE", f"{COPYRIGHT}\nNOT AN OPEN-SOURCE LICENCE\n")
    _write(root, "release_manifest.json", '{"deployment":{"streamlit":{"url":null}}}\n')
    for relative in (
        "COPYRIGHT.md", "NOTICE.md", "AUTHORS.md", "CITATION.cff", "CONTRIBUTING.md",
        "SECURITY.md", "docs/LICENSING_STATUS.md", "docs/OWNERSHIP_AND_ATTRIBUTION.md",
        "docs/THIRD_PARTY_LICENSES.md",
    ):
        _write(root, relative, "Public release fixture.\n")
    model = root / "models/newslens_synthetic_pipeline.joblib"
    model.parent.mkdir(parents=True, exist_ok=True)
    model.write_bytes(b"public synthetic model fixture")
    model_hash = hashlib.sha256(model.read_bytes()).hexdigest()
    calibration = {
        "model_sha256": model_hash,
        "method": "Platt scaling",
        "coefficient": 1.0,
        "intercept": 0.0,
        "editorial_review_threshold": 0.5,
        "model_version": "fixture",
    }
    calibration_path = root / "models/newslens_synthetic_calibration.json"
    calibration_path.write_text(json.dumps(calibration), encoding="utf-8")
    calibration_hash = hashlib.sha256(calibration_path.read_bytes()).hexdigest()
    manifest = {
        "synthetic_only": True,
        "artifacts": {
            "model": {"path": "models/newslens_synthetic_pipeline.joblib", "size_bytes": model.stat().st_size, "sha256": model_hash},
            "calibration": {"path": "models/newslens_synthetic_calibration.json", "size_bytes": calibration_path.stat().st_size, "sha256": calibration_hash, "bound_model_sha256": model_hash},
        },
    }
    _write(root, "models/public_artifact_manifest.json", json.dumps(manifest))
    archive = root / "data/synthetic/newslens-synthetic-articles-v1.0.0.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data/synthetic/newslens-synthetic-articles-v1.0.0.zip", archive)


def _run_release_audit(monkeypatch, root: Path, *, allow_gates: bool = True) -> int:
    monkeypatch.setattr(release_audit, "ROOT", root)
    monkeypatch.setattr(release_audit, "OUTPUT", root / "reports/results/public_release_scan.json")
    monkeypatch.setattr(release_audit, "MODEL", root / "models/newslens_synthetic_pipeline.joblib")
    monkeypatch.setattr(release_audit, "CALIBRATION", root / "models/newslens_synthetic_calibration.json")
    monkeypatch.setattr(release_audit, "ARTIFACT_MANIFEST", root / "models/public_artifact_manifest.json")
    monkeypatch.setattr(release_audit, "ARCHIVE", root / "data/synthetic/newslens-synthetic-articles-v1.0.0.zip")
    argv = ["audit_public_release.py"]
    if allow_gates:
        argv.append("--allow-publication-gates")
    monkeypatch.setattr(sys, "argv", argv)
    return release_audit.main()


def test_proprietary_ownership_package_and_synthetic_artifacts_are_complete() -> None:
    for name in ("LICENSE", "COPYRIGHT.md", "NOTICE.md", "AUTHORS.md", "CITATION.cff", "docs/LICENSING_STATUS.md", "models/public_artifact_manifest.json"):
        assert (ROOT / name).is_file()
    assert COPYRIGHT in _text("LICENSE")
    manifest = json.loads(_text("models/public_artifact_manifest.json"))
    assert manifest["synthetic_only"] is True
    assert not (ROOT / "models/fake_news_pipeline.joblib").exists()
    assert not (ROOT / "models/confidence_calibration.json").exists()


def test_citation_and_interface_identify_the_owner_and_synthetic_signal() -> None:
    citation = _text("CITATION.cff")
    assert 'family-names: "Gaikwad"' in citation
    assert 'given-names: "Deven Sachin"' in citation
    assert "date-released" not in citation and "doi:" not in citation and "orcid:" not in citation
    assert "Synthetic consistency signal" in _text("ui/components.py")
    assert "Synthetic Ledger-Consistency System" in _text("ui/navigation.py")
    assert AUTHOR in _text("web/app/layout.tsx")


def test_runtime_entrypoints_do_not_import_training_modules() -> None:
    runtime_files = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py")), *sorted((ROOT / "src").glob("*.py"))]
    findings = []
    for path in runtime_files:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
            names = [item.name for item in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            if any(name == "training" or name.startswith("training.") for name in names):
                findings.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert findings == []


def test_public_release_audit_passes_safe_fixture_with_only_deployment_gate(tmp_path: Path, monkeypatch, capsys) -> None:
    _minimal_release_tree(tmp_path)
    assert _run_release_audit(monkeypatch, tmp_path) == release_audit.EXIT_CLEAN
    captured = capsys.readouterr()
    assert "Public release audit: PASS" in captured.out
    report = json.loads(release_audit.OUTPUT.read_text(encoding="utf-8"))
    assert report["safe_tree_scan_passed"] is True
    assert report["artifact_integrity"]["passed"] is True
    assert report["publication_gates"] == ["Live Streamlit URL is unresolved."]


def test_public_release_audit_preserves_deployment_gate_exit(tmp_path: Path, monkeypatch) -> None:
    _minimal_release_tree(tmp_path)
    assert _run_release_audit(monkeypatch, tmp_path, allow_gates=False) == release_audit.EXIT_PUBLICATION_GATE


def test_public_release_audit_fails_closed_without_leaking_secret(tmp_path: Path, monkeypatch, capsys) -> None:
    _minimal_release_tree(tmp_path)
    secret = "gh" + "p_" + ("A" * 24)
    _write(tmp_path, f"{secret}.txt", f"before {secret} after")
    assert _run_release_audit(monkeypatch, tmp_path) == release_audit.EXIT_SAFETY_VIOLATION
    console = capsys.readouterr().out
    assert secret not in console


def test_public_release_audit_rejects_model_binding_mismatch(tmp_path: Path, monkeypatch) -> None:
    _minimal_release_tree(tmp_path)
    (tmp_path / "models/newslens_synthetic_pipeline.joblib").write_bytes(b"tampered")
    assert _run_release_audit(monkeypatch, tmp_path) == release_audit.EXIT_SAFETY_VIOLATION
