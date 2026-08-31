"""Fail closed on public-release secrets, private data and unresolved gates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "results" / "public_release_scan.json"
MODEL = ROOT / "models" / "fake_news_pipeline.joblib"

EXIT_CLEAN = 0
EXIT_PUBLICATION_GATE = 2
EXIT_SAFETY_VIOLATION = 3

PROHIBITED_PUBLIC_PATHS = {
    Path("models/confidence_calibration.json"),
    Path("models/fake_news_pipeline.joblib"),
}

FORBIDDEN_NAMES = {
    ".env",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "secrets.toml",
}
FORBIDDEN_PARTS = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vercel",
    "__pycache__",
    "downloads",
    "exports",
    "htmlcov",
    "logs",
    "node_modules",
    "playwright-report",
    "test-results",
    "uploads",
}
FORBIDDEN_SUFFIXES = {
    ".db", ".db-shm", ".db-wal", ".key", ".log", ".p12", ".pem",
    ".sqlite", ".sqlite3", ".tsbuildinfo", ".inspect.ndjson",
}
TEXT_SUFFIXES = {
    ".bat", ".cff", ".css", ".csv", ".html", ".ini", ".ipynb", ".js",
    ".json", ".jsx", ".md", ".mjs", ".py", ".sh", ".svg", ".toml",
    ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml",
}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_secret_assignment": re.compile(
        r"(?im)^\s*(?:api[_-]?key|password|secret|private[_-]?key|access[_-]?token|auth[_-]?token)"
        r"\s*[:=]\s*['\"](?!(?:example|placeholder|your-))[^'\"]{8,}['\"]"
    ),
}
LOCAL_PATH = re.compile(
    r"(?:[A-Za-z]:\\Users\\[^\\\s]+|/Users/[^/\s]+|/home/[^/\s]+|/workspace/[^\s]+|/root/[^\s]+)"
)
PERSONAL_DATA_PATTERNS = {
    "email_address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "labelled_phone_number": re.compile(
        r"(?i)\b(?:phone|mobile|telephone)\b.{0,24}(?:\+?\d[\d ()-]{7,}\d)"
    ),
    "student_identifier": re.compile(
        r"(?i)\b(?:student|roll|registration|enrolment|enrollment)[ _-]?(?:id|number|no\.?)"
        r"\s*[:=]\s*[A-Z0-9-]{4,}"
    ),
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def relative_files(*, tracked_only: bool = False) -> list[Path]:
    if not tracked_only:
        return sorted(path for path in ROOT.rglob("*") if path.is_file())

    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z", "--cached"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            "Tracked-file scanning requires a readable Git worktree."
        ) from exc

    tracked = completed.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return sorted(
        path
        for relative in tracked
        if relative and (path := ROOT / relative).is_file()
    )


def text_payloads(path: Path):
    if path.suffix.lower() in TEXT_SUFFIXES:
        yield path.read_text(encoding="utf-8", errors="ignore")
    elif path.suffix.lower() in {".docx", ".xlsx"}:
        with ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith(".xml") and name.startswith(("word/", "xl/", "docProps/")):
                    yield archive.read(name).decode("utf-8", errors="ignore")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-publication-gates",
        action="store_true",
        help="Return success when the tree is safe even though documented publication gates remain.",
    )
    parser.add_argument(
        "--tracked-files",
        action="store_true",
        help="Scan only Git-tracked files, excluding checkout metadata and untracked runner files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = relative_files(tracked_only=args.tracked_files)
    forbidden: list[str] = []
    secret_findings: list[dict[str, str]] = []
    personal_data_findings: list[dict[str, str]] = []
    local_paths: list[str] = []
    navigation_findings: list[str] = []
    broken_local_links: list[dict[str, str]] = []

    for path in files:
        relative = path.relative_to(ROOT)
        if (
            relative in PROHIBITED_PUBLIC_PATHS
            or path.name in FORBIDDEN_NAMES
            or any(part in FORBIDDEN_PARTS for part in relative.parts)
            or any(path.name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)
        ):
            forbidden.append(str(relative))
        if relative == Path("scripts/audit_public_release.py"):
            continue
        for payload in text_payloads(path):
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(payload):
                    secret_findings.append({"file": str(relative), "pattern": name})
            for name, pattern in PERSONAL_DATA_PATTERNS.items():
                if pattern.search(payload):
                    personal_data_findings.append(
                        {"file": str(relative), "pattern": name}
                    )
            if LOCAL_PATH.search(payload):
                local_paths.append(str(relative))

        if path.suffix.lower() == ".md":
            markdown = path.read_text(encoding="utf-8", errors="ignore")
            for raw_target in MARKDOWN_LINK.findall(markdown):
                target = raw_target.strip().strip("<>").split("#", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:", "/")):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    broken_local_links.append(
                        {"file": str(relative), "target": raw_target.strip()}
                    )

    runtime_navigation_files = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py")), *sorted((ROOT / "ui").glob("*.py"))]
    for path in runtime_navigation_files:
        text = path.read_text(encoding="utf-8")
        for pattern in ('target="_blank"', "window.open(", "st.link_button("):
            if pattern in text:
                navigation_findings.append(f"{path.relative_to(ROOT)}: {pattern}")

    placeholders = {"github_owner": [], "repository_url": [], "streamlit_url": [], "vercel_url": []}
    for path in files:
        relative = str(path.relative_to(ROOT))
        if relative == "scripts/audit_public_release.py" or relative.startswith("tests/"):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and relative != ".github/CODEOWNERS":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(token in text for token in ("[GITHUB_USERNAME]", "github.com/OWNER/NewsLens-AI")):
            placeholders["github_owner"].append(relative)
        if "[GITHUB_REPOSITORY_URL — TO BE PROVIDED]" in text:
            placeholders["repository_url"].append(relative)
        if any(token in text for token in ("YOUR-APP.streamlit.app", "[STREAMLIT_URL — TO BE PROVIDED]")):
            placeholders["streamlit_url"].append(relative)
        if "[VERCEL_URL — TO BE PROVIDED]" in text:
            placeholders["vercel_url"].append(relative)

    model_record = {
        "path": str(MODEL.relative_to(ROOT)),
        "exists": MODEL.exists(),
        "size_bytes": MODEL.stat().st_size if MODEL.exists() else None,
        "sha256": hashlib.sha256(MODEL.read_bytes()).hexdigest() if MODEL.exists() else None,
        "expected_artifact_id": "isot-tfidf-lr-v1.0.0",
        "blocked_from_git_by_gitignore": (
            "models/fake_news_pipeline.joblib"
            in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        ),
        "public_redistribution_rights_confirmed": False,
    }

    gates = []
    if placeholders["github_owner"] or placeholders["repository_url"]:
        gates.append("Exact GitHub owner/repository URL is unresolved.")
    if placeholders["streamlit_url"]:
        gates.append("Live Streamlit URL is unresolved.")
    if not model_record["public_redistribution_rights_confirmed"]:
        gates.append("Packaged model redistribution rights and explicit artifact license are unconfirmed.")
    if not (ROOT / ".git").exists():
        gates.append("Canonical Git history is unavailable for history-wide secret scanning.")

    required_legal_files = [
        "LICENSE",
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
        "release_manifest.json",
        ".gitattributes",
    ]
    missing_legal_files = [name for name in required_legal_files if not (ROOT / name).is_file()]
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8") if (ROOT / "LICENSE").exists() else ""
    legal_policy_passed = (
        not missing_legal_files
        and "All Rights Reserved" in license_text
        and "NOT AN OPEN-SOURCE LICENCE" in license_text
        and not (ROOT / "docs" / "LICENSE_RECOMMENDATION.md").exists()
    )
    safe_tree_scan_passed = (
        not forbidden
        and not secret_findings
        and not personal_data_findings
        and not local_paths
        and not broken_local_links
        and not navigation_findings
        and legal_policy_passed
    )

    report = {
        "release_root": ROOT.name,
        "files_scanned": len(files),
        "forbidden_files": sorted(set(forbidden)),
        "secret_findings": secret_findings,
        "personal_data_findings": personal_data_findings,
        "absolute_local_path_findings": sorted(set(local_paths)),
        "broken_local_markdown_links": broken_local_links,
        "internal_navigation_findings": navigation_findings,
        "deployment_placeholders": placeholders,
        "legal_policy": {
            "required_files_missing": missing_legal_files,
            "proprietary_notice_present": "All Rights Reserved" in license_text,
            "explicitly_not_open_source": "NOT AN OPEN-SOURCE LICENCE" in license_text,
            "superseded_license_recommendation_absent": not (ROOT / "docs" / "LICENSE_RECOMMENDATION.md").exists(),
            "passed": legal_policy_passed,
        },
        "model_artifact": model_record,
        "publication_gates": gates,
        "safe_tree_scan_passed": safe_tree_scan_passed,
        "public_release_ready": (
            safe_tree_scan_passed
            and not gates
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["safe_tree_scan_passed"]:
        return EXIT_SAFETY_VIOLATION
    if args.allow_publication_gates and report["safe_tree_scan_passed"]:
        return EXIT_CLEAN
    if report["publication_gates"]:
        return EXIT_PUBLICATION_GATE
    return EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main())
