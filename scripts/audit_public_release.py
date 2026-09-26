"""Fail closed on release secrets, private artifacts, and identity mismatches."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "results" / "public_release_scan.json"
MODEL = ROOT / "models" / "newslens_synthetic_pipeline.joblib"
CALIBRATION = ROOT / "models" / "newslens_synthetic_calibration.json"
ARTIFACT_MANIFEST = ROOT / "models" / "public_artifact_manifest.json"
ARCHIVE = ROOT / "data" / "synthetic" / "newslens-synthetic-articles-v1.0.0.zip"

ARCHIVE_SIZE = 10_319_934
ARCHIVE_SHA256 = "3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc"
ARCHIVE_GIT_BLOB = "cb0d5e57407be10fecefb34762e586bacd38dd56"

EXIT_CLEAN = 0
EXIT_PUBLICATION_GATE = 2
EXIT_SAFETY_VIOLATION = 3

PROHIBITED_PUBLIC_PATHS = {
    Path("models/fake_news_pipeline.joblib"),
    Path("models/confidence_calibration.json"),
}
FORBIDDEN_NAMES = {".env", "id_dsa", "id_ecdsa", "id_ed25519", "id_rsa", "secrets.toml"}
FORBIDDEN_PARTS = {
    ".git", ".idea", ".mypy_cache", ".next", ".pytest_cache", ".ruff_cache",
    ".venv", ".vercel", "__pycache__", "downloads", "exports", "htmlcov", "logs",
    "node_modules", "playwright-report", "test-results", "uploads",
}
FORBIDDEN_SUFFIXES = {
    ".db", ".db-shm", ".db-wal", ".key", ".log", ".p12", ".pem", ".sqlite",
    ".sqlite3", ".tsbuildinfo",
}
TEXT_SUFFIXES = {
    ".bat", ".cff", ".css", ".csv", ".html", ".ini", ".ipynb", ".js", ".json",
    ".jsx", ".md", ".mjs", ".py", ".sh", ".svg", ".toml", ".ts", ".tsx",
    ".txt", ".xml", ".yaml", ".yml",
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
RESERVED_TEST_EMAIL_DOMAINS = (".example", ".invalid", ".localhost", ".test")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CONSOLE_COUNT_FIELDS = (
    ("forbidden_files", "forbidden files"),
    ("secret_findings", "secret findings"),
    ("personal_data_findings", "personal-data findings"),
    ("absolute_local_path_findings", "absolute-path findings"),
    ("broken_local_markdown_links", "broken-link findings"),
    ("internal_navigation_findings", "navigation findings"),
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_id(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def _safe(value: str, label: str) -> str:
    sensitive = (
        any(pattern.search(value) for pattern in SECRET_PATTERNS.values())
        or any(pattern.search(value) for pattern in PERSONAL_DATA_PATTERNS.values())
        or LOCAL_PATH.search(value)
    )
    return value if not sensitive else f"[redacted-{label}:{hashlib.sha256(value.encode()).hexdigest()[:12]}]"


def contains_personal_data(name: str, pattern: re.Pattern[str], payload: str) -> bool:
    """Ignore only reserved-domain email fixtures; fail closed for every other match."""

    matches = list(pattern.finditer(payload))
    if name != "email_address":
        return bool(matches)
    return any(
        not match.group(0).lower().endswith(RESERVED_TEST_EMAIL_DOMAINS)
        for match in matches
    )


def relative_files(*, tracked_only: bool = False) -> list[Path]:
    if not tracked_only:
        return sorted(
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and not any(part in FORBIDDEN_PARTS for part in path.relative_to(ROOT).parts)
        )
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--cached"], cwd=ROOT, check=True, capture_output=True
    )
    return sorted(
        ROOT / name
        for name in completed.stdout.decode("utf-8", errors="surrogateescape").split("\0")
        if name and (ROOT / name).is_file()
    )


def text_payloads(path: Path):
    if path.suffix.lower() in TEXT_SUFFIXES:
        yield path.read_text(encoding="utf-8", errors="ignore")
    elif path.suffix.lower() in {".docx", ".xlsx"}:
        with ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith(".xml") and name.startswith(("word/", "xl/", "docProps/")):
                    yield archive.read(name).decode("utf-8", errors="ignore")


def artifact_evidence() -> dict[str, object]:
    evidence: dict[str, object] = {"passed": False}
    if not all(path.exists() for path in (MODEL, CALIBRATION, ARTIFACT_MANIFEST, ARCHIVE)):
        evidence["error"] = "One or more required public artifacts are missing."
        return evidence
    manifest = json.loads(ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    model_record = manifest["artifacts"]["model"]
    calibration_record = manifest["artifacts"]["calibration"]
    archive_record = {
        "path": str(ARCHIVE.relative_to(ROOT)),
        "size_bytes": ARCHIVE.stat().st_size,
        "sha256": file_sha256(ARCHIVE),
        "git_blob": git_blob_id(ARCHIVE),
    }
    checks = {
        "model_hash_matches_manifest": file_sha256(MODEL) == model_record["sha256"],
        "model_size_matches_manifest": MODEL.stat().st_size == model_record["size_bytes"],
        "calibration_hash_matches_manifest": file_sha256(CALIBRATION) == calibration_record["sha256"],
        "calibration_size_matches_manifest": CALIBRATION.stat().st_size == calibration_record["size_bytes"],
        "calibration_bound_to_model": calibration["model_sha256"] == model_record["sha256"] == calibration_record["bound_model_sha256"],
        "synthetic_only_declared": manifest.get("synthetic_only") is True,
        "archive_size_matches": archive_record["size_bytes"] == ARCHIVE_SIZE,
        "archive_sha256_matches": archive_record["sha256"] == ARCHIVE_SHA256,
        "archive_git_blob_matches": archive_record["git_blob"] == ARCHIVE_GIT_BLOB,
        "private_artifacts_absent": not any((ROOT / path).exists() for path in PROHIBITED_PUBLIC_PATHS),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "model_sha256": file_sha256(MODEL),
        "calibration_sha256": file_sha256(CALIBRATION),
        "archive": archive_record,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-publication-gates", action="store_true")
    parser.add_argument("--tracked-files", action="store_true")
    return parser.parse_args()


def _run_audit() -> int:
    args = parse_args()
    files = relative_files(tracked_only=args.tracked_files)
    forbidden: list[str] = []
    secrets: list[dict[str, str]] = []
    personal: list[dict[str, str]] = []
    local_paths: list[str] = []
    broken_links: list[dict[str, str]] = []
    navigation: list[str] = []
    for path in files:
        relative = path.relative_to(ROOT)
        if (
            relative in PROHIBITED_PUBLIC_PATHS
            or path.name in FORBIDDEN_NAMES
            or any(part in FORBIDDEN_PARTS for part in relative.parts)
            or any(path.name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)
        ):
            forbidden.append(_safe(str(relative), "path"))
        if relative == Path("scripts/audit_public_release.py") or relative == OUTPUT.relative_to(ROOT):
            continue
        for payload in text_payloads(path):
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(payload):
                    secrets.append({"file": _safe(str(relative), "path"), "pattern": name})
            for name, pattern in PERSONAL_DATA_PATTERNS.items():
                if contains_personal_data(name, pattern, payload):
                    personal.append({"file": _safe(str(relative), "path"), "pattern": name})
            if LOCAL_PATH.search(payload):
                local_paths.append(_safe(str(relative), "path"))
        if path.suffix.lower() == ".md":
            for raw in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8", errors="ignore")):
                target = raw.strip().strip("<>").split("#", 1)[0]
                if (
                    target
                    and not target.startswith(("http://", "https://", "mailto:", "/"))
                    and not (path.parent / target).resolve().exists()
                ):
                    broken_links.append(
                        {"file": _safe(str(relative), "path"), "target": _safe(raw, "target")}
                    )

    runtime_files = [
        ROOT / "app.py",
        *sorted((ROOT / "pages").glob("*.py")),
        *sorted((ROOT / "ui").glob("*.py")),
    ]
    for path in runtime_files:
        source = path.read_text(encoding="utf-8")
        for pattern in ('target="_blank"', "window.open(", "st.link_button("):
            if pattern in source:
                navigation.append(f"{path.relative_to(ROOT)}: {pattern}")

    license_text = (
        (ROOT / "LICENSE").read_text(encoding="utf-8") if (ROOT / "LICENSE").exists() else ""
    )
    required_legal = [
        "LICENSE", "COPYRIGHT.md", "NOTICE.md", "AUTHORS.md", "CITATION.cff",
        "CONTRIBUTING.md", "SECURITY.md", "docs/LICENSING_STATUS.md",
        "docs/OWNERSHIP_AND_ATTRIBUTION.md", "docs/THIRD_PARTY_LICENSES.md",
        "release_manifest.json", ".gitattributes",
    ]
    missing_legal = [name for name in required_legal if not (ROOT / name).is_file()]
    legal_passed = (
        not missing_legal
        and "All Rights Reserved" in license_text
        and "NOT AN OPEN-SOURCE LICENCE" in license_text
    )
    artifacts = artifact_evidence()
    release = (
        json.loads((ROOT / "release_manifest.json").read_text(encoding="utf-8"))
        if (ROOT / "release_manifest.json").exists()
        else {}
    )
    streamlit_url = release.get("deployment", {}).get("streamlit", {}).get("url")
    gates = (
        []
        if isinstance(streamlit_url, str)
        and streamlit_url.startswith("https://")
        and "streamlit.app" in streamlit_url
        else ["Live Streamlit URL is unresolved."]
    )
    safe = (
        not forbidden
        and not secrets
        and not personal
        and not local_paths
        and not broken_links
        and not navigation
        and legal_passed
        and bool(artifacts["passed"])
    )
    report = {
        "release_root": ROOT.name,
        "files_scanned": len(files),
        "forbidden_files": sorted(set(forbidden)),
        "secret_findings": secrets,
        "personal_data_findings": personal,
        "absolute_local_path_findings": sorted(set(local_paths)),
        "broken_local_markdown_links": broken_links,
        "internal_navigation_findings": navigation,
        "legal_policy": {"required_files_missing": missing_legal, "passed": legal_passed},
        "artifact_integrity": artifacts,
        "publication_gates": gates,
        "safe_tree_scan_passed": safe,
        "public_release_ready": safe and not gates,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not safe:
        exit_code = EXIT_SAFETY_VIOLATION
    elif args.allow_publication_gates or not gates:
        exit_code = EXIT_CLEAN
    else:
        exit_code = EXIT_PUBLICATION_GATE
    status = (
        "PASS" if exit_code == EXIT_CLEAN else "BLOCKED" if exit_code == EXIT_PUBLICATION_GATE else "FAIL"
    )
    print(f"Public release audit: {status}")
    print(f"Files scanned: {len(files)}")
    counts = {
        "forbidden_files": len(forbidden),
        "secret_findings": len(secrets),
        "personal_data_findings": len(personal),
        "absolute_local_path_findings": len(set(local_paths)),
        "broken_local_markdown_links": len(broken_links),
        "internal_navigation_findings": len(navigation),
    }
    for key, label in CONSOLE_COUNT_FIELDS:
        print(f"{label}: {counts[key]}")
    print(f"Publication gates: {len(gates)}")
    print(f"Exit status: {exit_code}")
    return exit_code


def main() -> int:
    try:
        return _run_audit()
    except Exception:
        print("Public release audit: ERROR", file=sys.stderr)
        print(
            "The audit could not complete safely. Inspect the failure locally; "
            "exception details are intentionally omitted from logs.",
            file=sys.stderr,
        )
        print(f"Exit status: {EXIT_SAFETY_VIOLATION}", file=sys.stderr)
        return EXIT_SAFETY_VIOLATION


if __name__ == "__main__":
    raise SystemExit(main())
