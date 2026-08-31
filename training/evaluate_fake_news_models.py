"""Validate and print the saved fake-news evaluation artefacts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    results = PROJECT_ROOT / "reports" / "results"
    required = [
        results / "model_metrics.json",
        results / "model_comparison.csv",
        results / "classification_report.csv",
    ]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing evaluation files: {', '.join(missing)}")
    metrics = json.loads(required[0].read_text(encoding="utf-8"))
    comparison = pd.read_csv(required[1])
    if comparison[["accuracy", "macro_f1", "roc_auc", "pr_auc"]].isna().any().any():
        raise ValueError("Model-comparison metrics contain missing values.")
    print(json.dumps(metrics, indent=2))
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
