"""Ownership, publication-gate, and release-security contracts."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Deven Sachin Gaikwad"
COPYRIGHT = "© 2026 Deven Sachin Gaikwad. All Rights Reserved."


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


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
