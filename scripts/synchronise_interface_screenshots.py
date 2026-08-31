"""Rebuild the integrity manifest for genuine Streamlit interface captures.

This helper never paints, crops, or otherwise edits screenshots. Canonical
captures are produced only by ``capture_streamlit_screenshots.py`` against a
running application; this script records their dimensions and hashes.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "reports" / "screenshots"
MANIFEST = ROOT / "reports" / "results" / "ui_screenshot_manifest.json"
EXPECTED_FILENAMES = (
    "01_home.png",
    "02_analysis_input.png",
    "03_summary_and_risk_results.png",
    "04_explainability_and_downloads.png",
    "05_editorial_review_required.png",
    "06_model_accountability.png",
    "07_model_benchmarking.png",
    "08_calibration_reliability.png",
    "09_dataset_analysis.png",
    "10_newsroom_analytics.png",
    "11_drift_readiness.png",
    "12_editorial_review_workflow.png",
    "13_research_about.png",
    "14_home_mobile.png",
    "15_analysis_mobile.png",
)


def rebuild_manifest(paths: list[Path]) -> None:
    captures: list[dict[str, object]] = []
    for path in paths:
        data = path.read_bytes()
        with Image.open(path) as image:
            width, height = image.size
        captures.append(
            {
                "filename": path.name,
                "width": width,
                "height": height,
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    evidence = {
        "interface_name": "NewsLens AI warm editorial newsroom",
        "design_system": "Warm editorial newsroom",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_css": "ui/theme.py::GLOBAL_CSS",
        "captures": captures,
    }
    MANIFEST.write_text(f"{json.dumps(evidence, indent=2)}\n", encoding="utf-8")


def main() -> None:
    paths = sorted(SCREENSHOTS.glob("*.png"))
    names = tuple(path.name for path in paths)
    if names != EXPECTED_FILENAMES:
        missing = sorted(set(EXPECTED_FILENAMES) - set(names))
        extra = sorted(set(names) - set(EXPECTED_FILENAMES))
        raise SystemExit(
            f"Canonical screenshot set mismatch; missing={missing}, extra={extra}."
        )
    for path in paths:
        print(f"indexed {path.name}")
    rebuild_manifest(paths)
    print(f"wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
