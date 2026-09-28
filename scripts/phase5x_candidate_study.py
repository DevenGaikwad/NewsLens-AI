"""One bounded Phase 5X candidate: fit only original training/calibration partitions.

Run after the confirmation seal and predeclared gate exist. This script never
trains on, selects on, or adjusts a threshold using either challenge set.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from statistics import median

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase5x_confirmation import SEAL_PATH, build_cases, case_hash
from src.calibration import CalibrationConfig
from src.fake_news_predictor import predict_credibility
from src.model_diagnostics import assess_input
from src.text_preprocessor import clean_article_text
from synthetic_benchmark.relational_signals import augment_relational_texts
from training.train_synthetic_model import ece, fit_calibration, load_dataset, metric_record, model_size, raw_scores, sigmoid


OUTPUT = ROOT / "reports/results/phase5x_candidate_study.json"


def fit() -> tuple[Pipeline, object, float, dict[str, object]]:
    frame = load_dataset()
    train = frame[frame["split"] == "training"]
    validation = frame[frame["split"] == "model_validation"]
    candidate = Pipeline([
        ("signals", FunctionTransformer(augment_relational_texts, validate=False)),
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.995, max_features=24_000, sublinear_tf=True)),
        ("classifier", LogisticRegression(C=2.0, max_iter=2_000, solver="liblinear", random_state=42)),
    ])
    candidate.fit(train["model_text"], train["target"])
    validation_probs = sigmoid(raw_scores(candidate, validation["model_text"]))
    validation_metrics = metric_record(validation["target"].to_numpy(), validation_probs)
    calibrator, threshold, policy = fit_calibration(candidate, frame)
    policy_rows = frame[frame["split"] == "abstention_policy"]
    policy_probs = calibrator.predict_proba(raw_scores(candidate, policy_rows["model_text"]).reshape(-1, 1))[:, 1]
    return candidate, calibrator, threshold, {
        "validation_balanced_accuracy": validation_metrics["balanced_accuracy"],
        "validation_macro_f1": validation_metrics["macro_f1"],
        "abstention_policy_brier": float(brier_score_loss(policy_rows["target"], policy_probs)),
        "threshold": threshold,
        "policy_table": policy,
        "original_training_rows": len(train),
        "calibration_rows": len(frame[frame["split"] == "calibration"]),
    }


def evaluate_once(candidate: Pipeline, calibrator: object, threshold: float) -> dict[str, object]:
    cases = build_cases()
    seal = json.loads(SEAL_PATH.read_text(encoding="utf-8"))
    assert case_hash(cases) == seal["case_set_sha256"]
    assert seal["source_sha256"] == __import__("hashlib").sha256((ROOT / "scripts/phase5x_confirmation.py").read_bytes()).hexdigest()
    config = CalibrationConfig(
        method="Platt scaling", coefficient=float(calibrator.coef_[0, 0]),
        intercept=float(calibrator.intercept_[0]), editorial_review_threshold=threshold,
        model_sha256="candidate-not-published", model_version="phase5x-experimental",
        calibration_rows=1200, threshold_policy_rows=1200, final_test_rows=0,
    )
    rows = []
    for case in cases:
        cleaned = clean_article_text(case["text"], remove_source_markers=False)
        diagnostics = assess_input(cleaned, candidate)
        result = predict_credibility(cleaned, candidate, calibration=config, diagnostics=diagnostics)
        automatic = not result.review_required and not diagnostics.domain_mismatch and not result.score_withheld
        public_score = not diagnostics.domain_mismatch and not result.score_withheld
        rows.append({"id": case["id"], "event": case["event"], "category": case["category"],
                     "expected": case["expected"], "raw_class": result.predicted_class,
                     "probability_conflict": result.misleading_probability if public_score else None,
                     "raw_probability_conflict": result.misleading_probability,
                     "automatic": automatic, "review": result.review_required,
                     "score_withheld": not public_score, "ms": result.processing_time_seconds * 1000})
    structured = [row for row in rows if row["expected"] != "review"]
    labels = np.asarray([int(row["expected"] == "conflict") for row in structured])
    predictions = np.asarray([int(row["raw_class"] == "misleading") for row in structured])
    probs = np.asarray([row["raw_probability_conflict"] for row in structured])
    precision, recall, f1, support = precision_recall_fscore_support(labels, predictions, labels=[0, 1], zero_division=0)
    auto = [row for row in structured if row["automatic"]]
    auto_precision = {}
    for expected, predicted in (("agree", "reliable"), ("conflict", "misleading")):
        selected = [row for row in auto if row["raw_class"] == predicted]
        auto_precision[expected] = sum(row["expected"] == expected for row in selected) / len(selected) if selected else None
    flips = 0
    for event in {row["event"] for row in structured}:
        pair = [row for row in structured if row["event"] == event]
        exact = next(row for row in pair if row["category"] == "exact agreement")
        single = next(row for row in pair if row["category"] == "single-field counterfactual")
        flips += exact["raw_class"] != single["raw_class"]
    reviews = [row for row in rows if row["expected"] == "review"]
    return {"cases_sha256": seal["case_set_sha256"], "class_order": ["agree", "conflict"],
            "confusion_matrix": confusion_matrix(labels, predictions, labels=[0, 1]).tolist(),
            "precision": precision.tolist(), "recall": recall.tolist(), "f1": f1.tolist(), "support": support.tolist(),
            "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
            "macro_f1": float(f1_score(labels, predictions, average="macro")),
            "brier": float(brier_score_loss(labels, probs)), "ece_10": ece(labels, probs),
            "automatic_coverage": len(auto) / len(structured), "automatic_precision": auto_precision,
            "counterfactual_flips": flips, "counterfactual_pairs": len({row["event"] for row in structured}),
            "expected_reviews_routed": sum(row["review"] for row in reviews), "expected_reviews_total": len(reviews),
            "reviews_scores_withheld": all(row["score_withheld"] for row in reviews),
            "ordinary_scores_withheld": all(row["score_withheld"] for row in reviews if row["category"] == "ordinary prose"),
            "median_inference_ms": median(row["ms"] for row in rows), "model_size_bytes": model_size(candidate),
            "cases": rows}


def gate(dev: dict[str, object], confirmation: dict[str, object]) -> dict[str, bool]:
    c = confirmation
    return {
        "validation_balanced_accuracy": dev["validation_balanced_accuracy"] >= .99,
        "validation_macro_f1": dev["validation_macro_f1"] >= .99,
        "policy_brier": dev["abstention_policy_brier"] <= .01,
        "agree_recall": c["recall"][0] >= .90,
        "conflict_recall": c["recall"][1] >= .90,
        "balanced_accuracy": c["balanced_accuracy"] >= .90,
        "macro_f1": c["macro_f1"] >= .90,
        "brier": c["brier"] <= .10,
        "ece": c["ece_10"] <= .10,
        "automatic_coverage": c["automatic_coverage"] >= .80,
        "agreement_auto_precision": c["automatic_precision"]["agree"] is not None and c["automatic_precision"]["agree"] >= .95,
        "conflict_auto_precision": c["automatic_precision"]["conflict"] is not None and c["automatic_precision"]["conflict"] >= .95,
        "counterfactual_flips": c["counterfactual_flips"] >= 11,
        "review_routing": c["expected_reviews_routed"] == c["expected_reviews_total"] == 12,
        "review_score_withholding": c["reviews_scores_withheld"] and c["ordinary_scores_withheld"],
        "latency": c["median_inference_ms"] <= 15,
        "package_size": c["model_size_bytes"] <= 1024 * 1024,
    }


if __name__ == "__main__":
    assert SEAL_PATH.exists() and (ROOT / "docs/PHASE5X_MODEL_GATE.md").exists(), "Seal and gate must precede candidate evaluation."
    candidate, calibrator, threshold, dev = fit()
    if dev["validation_balanced_accuracy"] < .99 or dev["validation_macro_f1"] < .99 or dev["abstention_policy_brier"] > .01:
        report = {"decision": "reject-before-confirmation", "development": dev}
    else:
        confirmation = evaluate_once(candidate, calibrator, threshold)
        results = gate(dev, confirmation)
        report = {"decision": "eligible-for-release-gates" if all(results.values()) else "reject",
                  "development": dev, "confirmation": confirmation, "predeclared_gate": results}
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "confirmation"}, indent=2)[:2500])
    if "confirmation" in report:
        print(json.dumps({key: value for key, value in report["confirmation"].items() if key != "cases"}, indent=2))
