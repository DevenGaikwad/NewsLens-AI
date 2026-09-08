"""Ownership, publication-gate, and release-security contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path
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
    _write(root, ".gitignore", "models/fake_news_pipeline.joblib\n")
    _write(root, ".gitattributes")
    _write(root, "LICENSE", "All Rights Reserved\nNOT AN OPEN-SOURCE LICENCE\n")
    _write(root, "release_manifest.json", "{}\n")
    for relative in (
        "COPYRIGHT.md",
        "NOTICE.md",
        "AUTHORS.md",
        "CITATION.cff",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "docs/LICENSING_STATUS.md",
        "docs/OWNERSHIP_AND_ATTRIBUTION.md",
        "docs/THIRD_PARTY_LICENSES.md",
        "docs/DEPLOYMENT_CHECKPOINT.md",
    ):
        _write(root, relative, "Public release fixture.\n")


def _run_release_audit(monkeypatch, root: Path, *, allow_gates: bool = True) -> int:
    monkeypatch.setattr(release_audit, "ROOT", root)
    monkeypatch.setattr(
        release_audit,
        "OUTPUT",
        root / "reports" / "results" / "public_release_scan.json",
    )
    monkeypatch.setattr(
        release_audit, "MODEL", root / "models" / "fake_news_pipeline.joblib"
    )
    argv = ["audit_public_release.py"]
    if allow_gates:
        argv.append("--allow-publication-gates")
    monkeypatch.setattr(sys, "argv", argv)
    return release_audit.main()


def test_proprietary_ownership_package_is_complete() -> None:
    required = (
        "LICENSE",
        "COPYRIGHT.md",
        "NOTICE.md",
        "AUTHORS.md",
        "CITATION.cff",
        ".gitattributes",
        "docs/LICENSING_STATUS.md",
        "docs/OWNERSHIP_AND_ATTRIBUTION.md",
        "docs/THIRD_PARTY_LICENSES.md",
        "docs/DEPLOYMENT_CHECKPOINT.md",
        "release_manifest.json",
    )
    assert all((ROOT / name).is_file() for name in required)
    license_text = _text("LICENSE")
    assert COPYRIGHT in license_text
    assert "NOT AN OPEN-SOURCE LICENCE" in license_text
    assert not (ROOT / "docs/LICENSE_RECOMMENDATION.md").exists()


def test_citation_metadata_identifies_the_confirmed_author_without_fake_ids() -> None:
    citation = _text("CITATION.cff")
    assert 'family-names: "Gaikwad"' in citation
    assert 'given-names: "Deven Sachin"' in citation
    assert 'title: "NewsLens AI"' in citation
    assert "date-released" not in citation
    assert "doi:" not in citation and "orcid:" not in citation


def test_streamlit_and_web_show_required_attribution() -> None:
    components = _text("ui/components.py")
    navigation = _text("ui/navigation.py")
    research = _text("pages/05_Research_About.py")
    visualizations = _text("src/visualizations.py")
    layout = _text("web/app/layout.tsx")
    assert "Designed and developed by" in components
    assert "Editorial Credibility-Risk System" in navigation
    assert "Editorial Fact-Checking System" not in navigation
    assert "Ownership and Academic Integrity" in research
    assert '"text": ""' in visualizations
    assert AUTHOR in layout and COPYRIGHT in layout


def test_model_stays_git_ignored_and_public_deployment_is_blocked() -> None:
    ignored = _text(".gitignore").splitlines()
    assert "models/fake_news_pipeline.joblib" in ignored
    assert "models/confidence_calibration.json" in ignored
    block = _text("PUBLIC_DEPLOYMENT_BLOCKED.md")
    assert "excludes" in block and "public deployment remains blocked" in block.lower()
    decision = _text("docs/MODEL_REDISTRIBUTION_DECISION.md")
    assert "permission unclear" in decision.lower()
    assert "Download availability alone" in decision


def test_runtime_entrypoints_do_not_import_training_modules() -> None:
    runtime_files = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py")), *sorted((ROOT / "src").glob("*.py"))]
    findings = []
    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(text, filename=str(path))):
            if isinstance(node, ast.Import):
                names = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            if any(name == "training" or name.startswith("training.") for name in names):
                findings.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert findings == []


def test_internal_streamlit_navigation_has_no_new_tab_mechanisms() -> None:
    runtime_files = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py")), *sorted((ROOT / "ui").glob("*.py"))]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in runtime_files)
    assert 'target="_blank"' not in combined
    assert "window.open(" not in combined
    assert "st.link_button(" not in combined


def test_web_embed_has_origin_policy_headers_and_sandbox() -> None:
    policy = _text("web/url-policy.ts")
    config = _text("web/next.config.ts")
    frame = _text("web/app/app/EmbedFrame.tsx")
    assert 'parsed.protocol !== "https:"' in policy
    assert "streamlit\\.app" in policy
    for header in (
        "Content-Security-Policy",
        "Referrer-Policy",
        "Permissions-Policy",
        "X-Content-Type-Options",
        "Strict-Transport-Security",
    ):
        assert header in config
    assert "frame-src ${streamlitOrigin}" in config
    assert 'sandbox="allow-downloads allow-forms allow-popups allow-same-origin allow-scripts"' in frame


def test_public_environment_examples_contain_no_secret_values() -> None:
    root_example = _text(".env.example")
    web_example = _text("web/.env.example")
    assert "NEXT_PUBLIC_STREAMLIT_APP_URL=https://YOUR-APP.streamlit.app" in web_example
    assert "PASSWORD=" not in root_example.upper()
    assert "TOKEN=" not in root_example.upper()
    assert "SECRET=" not in root_example.upper()


def test_public_release_audit_emits_only_safe_clean_summary(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _minimal_release_tree(tmp_path)

    exit_code = _run_release_audit(monkeypatch, tmp_path)
    captured = capsys.readouterr()

    assert exit_code == release_audit.EXIT_CLEAN
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "Public release audit: PASS",
        "Files scanned: 15",
        "forbidden files: 0",
        "secret findings: 0",
        "personal-data findings: 0",
        "absolute-path findings: 0",
        "broken-link findings: 0",
        "navigation findings: 0",
        "Publication gates: 1",
        "Exit status: 0",
    ]

    report = json.loads(release_audit.OUTPUT.read_text(encoding="utf-8"))
    assert set(report) == {
        "release_root",
        "files_scanned",
        "forbidden_files",
        "secret_findings",
        "personal_data_findings",
        "absolute_local_path_findings",
        "broken_local_markdown_links",
        "internal_navigation_findings",
        "deployment_placeholders",
        "legal_policy",
        "model_artifact",
        "publication_gates",
        "safe_tree_scan_passed",
        "public_release_ready",
    }
    assert report["safe_tree_scan_passed"] is True


def test_public_release_audit_fails_without_leaking_findings(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _minimal_release_tree(tmp_path)
    synthetic_secret = "gh" + "p_" + ("A" * 24)
    personal_value = "fixture.person" + "@" + "example.invalid"
    local_value = "/" + "workspace" + "/private-user/private-dataset.csv"
    surrounding_content = f"confidential-before {synthetic_secret} confidential-after"
    sensitive_filename = f"{synthetic_secret}.txt"

    _write(tmp_path, ".env", "safe fixture\n")
    _write(tmp_path, sensitive_filename, surrounding_content)
    _write(tmp_path, "personal.txt", personal_value)
    _write(tmp_path, "local-path.txt", local_value)
    _write(tmp_path, "broken.md", "[missing](not-present.md)\n")

    exit_code = _run_release_audit(monkeypatch, tmp_path)
    captured = capsys.readouterr()
    combined_console = captured.out + captured.err

    assert exit_code == release_audit.EXIT_SAFETY_VIOLATION
    assert captured.err == ""
    assert "Public release audit: FAIL" in captured.out
    assert "forbidden files: 1" in captured.out
    assert "secret findings: 1" in captured.out
    assert "personal-data findings: 1" in captured.out
    assert "absolute-path findings: 1" in captured.out
    assert "broken-link findings: 1" in captured.out
    assert "Exit status: 3" in captured.out
    for sensitive_value in (
        synthetic_secret,
        personal_value,
        local_value,
        surrounding_content,
        sensitive_filename,
        str(tmp_path),
        "confidential-before",
        "confidential-after",
    ):
        assert sensitive_value not in combined_console

    report = json.loads(release_audit.OUTPUT.read_text(encoding="utf-8"))
    assert report["safe_tree_scan_passed"] is False
    assert report["secret_findings"] == [
        {
            "file": report["secret_findings"][0]["file"],
            "pattern": "github_token",
        }
    ]
    assert report["secret_findings"][0]["file"].startswith("[redacted-path:")
    assert synthetic_secret not in json.dumps(report)


def test_public_release_audit_preserves_publication_gate_exit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _minimal_release_tree(tmp_path)

    exit_code = _run_release_audit(
        monkeypatch, tmp_path, allow_gates=False
    )
    captured = capsys.readouterr()

    assert exit_code == release_audit.EXIT_PUBLICATION_GATE
    assert captured.err == ""
    assert "Public release audit: BLOCKED" in captured.out
    assert "Publication gates: 1" in captured.out
    assert "Exit status: 2" in captured.out


def test_public_release_audit_omits_sensitive_exception_details(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _minimal_release_tree(tmp_path)
    synthetic_secret = "AK" + "IA" + ("B" * 16)
    sensitive_filename = f"{synthetic_secret}.docx"
    (tmp_path / sensitive_filename).write_bytes(b"not a valid office archive")

    exit_code = _run_release_audit(monkeypatch, tmp_path)
    captured = capsys.readouterr()
    combined_console = captured.out + captured.err

    assert exit_code == release_audit.EXIT_SAFETY_VIOLATION
    assert captured.out == ""
    assert captured.err.splitlines() == [
        "Public release audit: ERROR",
        (
            "The audit could not complete safely. Inspect the failure locally; "
            "exception details are intentionally omitted from logs."
        ),
        "Exit status: 3",
    ]
    assert synthetic_secret not in combined_console
    assert sensitive_filename not in combined_console
    assert str(tmp_path) not in combined_console
