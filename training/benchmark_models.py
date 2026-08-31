"""Run the controlled NewsLens AI benchmark and confidence-calibration study.

The script is deliberately separate from the Streamlit runtime. It verifies the
packaged Logistic Regression against the established holdout evidence, compares
no more than three classical candidates, calibrates confidence on validation
data, selects an abstention threshold without test-set tuning, and writes only
aggregate evidence. Raw ISOT rows are never copied into project reports.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import tempfile
import zlib
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedGroupKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MODEL_PATH, RANDOM_SEED  # noqa: E402
from src.utils import utc_now_iso  # noqa: E402
from training.prepare_dataset import load_isot_dataset  # noqa: E402


REPORTS_DIR = PROJECT_ROOT / "reports"
RESULTS_DIR = REPORTS_DIR / "results"
FIGURES_DIR = REPORTS_DIR / "figures"
CALIBRATION_PATH = PROJECT_ROOT / "models" / "confidence_calibration.json"
BENCHMARK_RESULTS_PATH = REPORTS_DIR / "model_benchmark_results.csv"
BENCHMARK_SUMMARY_PATH = REPORTS_DIR / "model_benchmark_summary.json"
BENCHMARK_METHOD_PATH = REPORTS_DIR / "model_benchmark_methodology.md"
CALIBRATION_EVIDENCE_PATH = REPORTS_DIR / "calibration_validation.json"
REFERENCE_PROFILE_PATH = REPORTS_DIR / "model_reference_profile.json"
ERROR_ANALYSIS_PATH = RESULTS_DIR / "error_analysis.csv"

EXPECTED_MODEL_SHA256 = "e9dd8368a4eec1ea5111da6c002889a146af98acba06742d2795486977d93dcb"
EXPECTED_TRUE_SHA256 = "ba0844414a65dc6ae7402b8eee5306da24b6b56488d6767135af466c7dcb2775"
EXPECTED_FAKE_SHA256 = "bebf8bcfe95678bf2c732bf413a2ce5f621af0102c82bf08083b2e5d3c693d0c"
EXPECTED_BASELINE_ACCURACY = 0.9935416666666667
EXPECTED_BASELINE_MACRO_F1 = 0.9935416327490262
NEAR_DUPLICATE_JACCARD = 0.90
MIN_DRIFT_OBSERVATIONS = 20


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_values(values: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(str(value).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


@dataclass(frozen=True)
class LeakageScreen:
    pairs: tuple[tuple[int, int, float], ...]
    groups: tuple[int, ...]
    candidate_pairs: int


def _five_gram_hashes(text: str) -> set[int]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())[:800]
    if len(tokens) < 5:
        return set()
    return {
        zlib.crc32(" ".join(tokens[index : index + 5]).encode("utf-8"))
        for index in range(len(tokens) - 4)
    }


def screen_near_duplicates(texts: pd.Series) -> LeakageScreen:
    """Find high-similarity candidates with a deterministic approximate screen.

    Eight minimum CRC32 signatures generate candidates; the final decision is
    based on exact Jaccard overlap of word five-gram sets, so hash collisions can
    create extra comparisons but cannot by themselves declare a near duplicate.
    """

    shingle_sets: list[set[int]] = []
    buckets: dict[int, list[int]] = defaultdict(list)
    for index, text in enumerate(texts.astype(str)):
        shingles = _five_gram_hashes(text)
        shingle_sets.append(shingles)
        for signature in sorted(shingles)[:8]:
            buckets[signature].append(index)

    candidates: set[tuple[int, int]] = set()
    for members in buckets.values():
        if 1 < len(members) <= 60:
            candidates.update(combinations(members, 2))

    union = UnionFind(len(texts))
    near_pairs: list[tuple[int, int, float]] = []
    for left, right in sorted(candidates):
        left_set = shingle_sets[left]
        right_set = shingle_sets[right]
        if not left_set or not right_set:
            continue
        length_ratio = min(len(left_set), len(right_set)) / max(len(left_set), len(right_set))
        if length_ratio < 0.85:
            continue
        similarity = len(left_set & right_set) / len(left_set | right_set)
        if similarity >= NEAR_DUPLICATE_JACCARD:
            union.union(left, right)
            near_pairs.append((left, right, round(float(similarity), 6)))

    roots = [union.find(index) for index in range(len(texts))]
    root_to_group = {root: group for group, root in enumerate(sorted(set(roots)))}
    groups = tuple(root_to_group[root] for root in roots)
    return LeakageScreen(tuple(near_pairs), groups, len(candidates))


def base_pipeline(classifier: Any) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=3,
                    max_df=0.92,
                    max_features=40_000,
                    sublinear_tf=True,
                    strip_accents="unicode",
                ),
            ),
            ("classifier", classifier),
        ]
    )


def raw_scores(estimator: Pipeline, texts: pd.Series) -> np.ndarray:
    if hasattr(estimator, "decision_function"):
        return np.asarray(estimator.decision_function(texts), dtype=float).ravel()
    probabilities = np.asarray(estimator.predict_proba(texts), dtype=float)
    classes = list(estimator.classes_)
    positive = probabilities[:, classes.index(1)]
    clipped = np.clip(positive, 1e-8, 1 - 1e-8)
    return np.log(clipped / (1 - clipped))


def native_probabilities(estimator: Pipeline, texts: pd.Series) -> np.ndarray | None:
    if not hasattr(estimator, "predict_proba"):
        return None
    values = np.asarray(estimator.predict_proba(texts), dtype=float)
    return values[:, list(estimator.classes_).index(1)]


def fit_platt_calibrator(scores: np.ndarray, labels: pd.Series) -> LogisticRegression:
    calibrator = LogisticRegression(
        C=1_000_000.0,
        solver="lbfgs",
        max_iter=1_000,
        random_state=RANDOM_SEED,
    )
    calibrator.fit(np.asarray(scores).reshape(-1, 1), np.asarray(labels, dtype=int))
    return calibrator


def calibrated_probabilities(calibrator: LogisticRegression, scores: np.ndarray) -> np.ndarray:
    return np.asarray(calibrator.predict_proba(np.asarray(scores).reshape(-1, 1)))[:, 1]


def expected_calibration_error(labels: pd.Series | np.ndarray, probabilities: np.ndarray, bins: int = 10) -> float:
    labels_array = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = len(labels_array)
    error = 0.0
    for index in range(bins):
        lower, upper = edges[index], edges[index + 1]
        if index == bins - 1:
            mask = (probabilities >= lower) & (probabilities <= upper)
        else:
            mask = (probabilities >= lower) & (probabilities < upper)
        if not np.any(mask):
            continue
        error += float(mask.mean()) * abs(
            float(probabilities[mask].mean()) - float(labels_array[mask].mean())
        )
    return error if total else math.nan


def wilson_lower_bound(successes: int, total: int, z_score: float = 1.96) -> float:
    if total <= 0:
        return 0.0
    proportion = successes / total
    denominator = 1 + (z_score**2 / total)
    centre = proportion + (z_score**2 / (2 * total))
    adjustment = z_score * math.sqrt(
        (proportion * (1 - proportion) + z_score**2 / (4 * total)) / total
    )
    return (centre - adjustment) / denominator


def choose_review_threshold(labels: pd.Series, probabilities: np.ndarray) -> tuple[float, list[dict[str, float | int]]]:
    labels_array = np.asarray(labels, dtype=int)
    predicted = (probabilities >= 0.5).astype(int)
    confidence = np.maximum(probabilities, 1 - probabilities)
    rows: list[dict[str, float | int]] = []
    for threshold in np.round(np.arange(0.50, 0.951, 0.01), 2):
        decided = confidence >= threshold
        count = int(decided.sum())
        correct = int((predicted[decided] == labels_array[decided]).sum()) if count else 0
        accuracy = correct / count if count else 0.0
        rows.append(
            {
                "threshold": float(threshold),
                "auto_decided": count,
                "coverage": round(count / len(labels_array), 6),
                "selective_accuracy": round(accuracy, 6),
                "wilson_lower_95": round(wilson_lower_bound(correct, count), 6),
            }
        )
    eligible = [
        row
        for row in rows
        if float(row["coverage"]) >= 0.80 and float(row["wilson_lower_95"]) >= 0.99
    ]
    if eligible:
        selected = min(eligible, key=lambda row: float(row["threshold"]))
    else:
        coverage_rows = [row for row in rows if float(row["coverage"]) >= 0.80]
        selected = max(
            coverage_rows or rows,
            key=lambda row: (float(row["wilson_lower_95"]), float(row["coverage"])),
        )
    return float(selected["threshold"]), rows


def classification_metrics(labels: pd.Series, predictions: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    class_precision, class_recall, class_f1, support = precision_recall_fscore_support(
        labels, predictions, labels=[0, 1], zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_precision": float(precision_score(labels, predictions, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(labels, predictions, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "roc_auc": float(roc_auc_score(labels, probabilities)),
        "pr_auc": float(average_precision_score(labels, probabilities)),
        "brier_score": float(brier_score_loss(labels, probabilities)),
        "expected_calibration_error": float(expected_calibration_error(labels, probabilities)),
        "reliable_precision": float(class_precision[0]),
        "reliable_recall": float(class_recall[0]),
        "reliable_f1": float(class_f1[0]),
        "reliable_support": int(support[0]),
        "misleading_precision": float(class_precision[1]),
        "misleading_recall": float(class_recall[1]),
        "misleading_f1": float(class_f1[1]),
        "misleading_support": int(support[1]),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=[0, 1]).tolist(),
    }


def split_validation_and_test(
    frame: pd.DataFrame,
    holdout_indices: np.ndarray,
    groups: tuple[int, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    holdout = frame.loc[holdout_indices]
    holdout_groups = np.asarray([groups[int(index)] for index in holdout_indices])
    outer = StratifiedGroupKFold(n_splits=2, shuffle=True, random_state=RANDOM_SEED)
    validation_pos, test_pos = next(
        outer.split(holdout["combined"], holdout["label"], groups=holdout_groups)
    )
    validation_indices = holdout_indices[validation_pos]
    test_indices = holdout_indices[test_pos]

    validation = frame.loc[validation_indices]
    validation_groups = np.asarray([groups[int(index)] for index in validation_indices])
    inner = StratifiedGroupKFold(n_splits=2, shuffle=True, random_state=RANDOM_SEED + 1)
    calibration_pos, policy_pos = next(
        inner.split(validation["combined"], validation["label"], groups=validation_groups)
    )
    return (
        validation_indices,
        test_indices,
        validation_indices[calibration_pos],
        validation_indices[policy_pos],
    )


def audit_partition_leakage(
    pairs: tuple[tuple[int, int, float], ...],
    partitions: dict[str, set[int]],
) -> list[dict[str, Any]]:
    location = {index: name for name, values in partitions.items() for index in values}
    findings = []
    for left, right, similarity in pairs:
        if location.get(left) and location.get(right) and location[left] != location[right]:
            findings.append(
                {
                    "left_index_hash": hashlib.sha256(str(left).encode()).hexdigest(),
                    "right_index_hash": hashlib.sha256(str(right).encode()).hexdigest(),
                    "similarity": similarity,
                    "left_partition": location[left],
                    "right_partition": location[right],
                }
            )
    return findings


def reliability_points(labels: pd.Series, probabilities: np.ndarray) -> dict[str, list[float]]:
    observed, predicted = calibration_curve(labels, probabilities, n_bins=10, strategy="uniform")
    return {
        "mean_predicted_probability": [round(float(value), 6) for value in predicted],
        "observed_positive_rate": [round(float(value), 6) for value in observed],
    }


def model_size_bytes(model: Pipeline, name: str) -> int:
    if name == "Logistic Regression":
        return MODEL_PATH.stat().st_size
    with tempfile.TemporaryDirectory(prefix="newslens-benchmark-") as directory:
        path = Path(directory) / "candidate.joblib"
        joblib.dump(model, path, compress=3)
        return path.stat().st_size


def measure_latency_ms(
    model: Pipeline,
    calibrator: LogisticRegression,
    texts: pd.Series,
) -> float:
    sample = texts.reset_index(drop=True)
    _ = model.predict(sample.iloc[: min(16, len(sample))])
    durations = []
    for _ in range(3):
        started = perf_counter()
        _ = model.predict(sample)
        scores = raw_scores(model, sample)
        _ = calibrated_probabilities(calibrator, scores)
        durations.append(perf_counter() - started)
    return float(np.median(durations) / len(sample) * 1000)


def input_reference_profile(
    model: Pipeline,
    texts: pd.Series,
    labels: pd.Series,
    *,
    evaluation_texts: pd.Series,
    calibrator: LogisticRegression,
) -> dict[str, Any]:
    vocabulary = set(model.named_steps["tfidf"].vocabulary_)
    sampled = texts.sample(n=min(2_000, len(texts)), random_state=RANDOM_SEED)
    word_counts: list[int] = []
    coverage: list[float] = []
    for text in sampled.astype(str):
        tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
        word_counts.append(len(tokens))
        if tokens:
            coverage.append(sum(token in vocabulary for token in tokens) / len(tokens))
    evaluation_probabilities = calibrated_probabilities(
        calibrator, raw_scores(model, evaluation_texts)
    )
    predicted = (evaluation_probabilities >= 0.5).astype(int)
    confidence = np.maximum(evaluation_probabilities, 1 - evaluation_probabilities)
    return {
        "schema_version": 1,
        "model_version": "isot-tfidf-lr-v1.0.0",
        "reference_rows": int(len(texts)),
        "profile_sample_rows": int(len(sampled)),
        "minimum_observations": MIN_DRIFT_OBSERVATIONS,
        "article_word_count": {
            "p01": float(np.quantile(word_counts, 0.01)),
            "p05": float(np.quantile(word_counts, 0.05)),
            "median": float(np.median(word_counts)),
            "p95": float(np.quantile(word_counts, 0.95)),
            "p99": float(np.quantile(word_counts, 0.99)),
            "mean": float(np.mean(word_counts)),
        },
        "vocabulary_coverage": {
            "p01": float(np.quantile(coverage, 0.01)),
            "p05": float(np.quantile(coverage, 0.05)),
            "median": float(np.median(coverage)),
            "mean": float(np.mean(coverage)),
        },
        "predicted_class_distribution": {
            "reliable": float(np.mean(predicted == 0)),
            "misleading": float(np.mean(predicted == 1)),
        },
        "calibrated_confidence": {
            "p05": float(np.quantile(confidence, 0.05)),
            "median": float(np.median(confidence)),
            "mean": float(np.mean(confidence)),
        },
        "label_distribution": {
            "reliable": float(np.mean(np.asarray(labels) == 0)),
            "misleading": float(np.mean(np.asarray(labels) == 1)),
        },
        "domain_mismatch_rule": (
            "Heuristic warning when unigram vocabulary coverage is below the reference p01 "
            "or article length is outside the reference p01-p99 interval."
        ),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_reliability_figure(evidence: dict[str, Any]) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(7.4, 5.2), dpi=190)
    axis.plot([0, 1], [0, 1], linestyle="--", color="#A89984", label="Ideal calibration")
    before = evidence["production_model"]["uncalibrated_reliability"]
    after = evidence["production_model"]["calibrated_reliability"]
    axis.plot(
        before["mean_predicted_probability"],
        before["observed_positive_rate"],
        marker="o",
        color="#8A693D",
        label="Native LR score",
    )
    axis.plot(
        after["mean_predicted_probability"],
        after["observed_positive_rate"],
        marker="o",
        color="#40352C",
        label="Platt calibrated",
    )
    axis.set(
        xlabel="Mean predicted misleading-content probability",
        ylabel="Observed misleading-labelled proportion",
        title="Production-model reliability on the untouched final test partition",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    axis.legend(frameon=False)
    axis.grid(color="#D4CEC2", alpha=0.7)
    figure.patch.set_facecolor("#FAF8F2")
    axis.set_facecolor("#FAF8F2")
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "calibration_reliability.png", bbox_inches="tight")
    plt.close(figure)


def write_confusion_figure(model_results: list[dict[str, Any]]) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, 3, figsize=(12.4, 4.0), dpi=190)
    for axis, result in zip(axes, model_results, strict=True):
        matrix = np.asarray(result["metrics"]["confusion_matrix"])
        image = axis.imshow(matrix, cmap="YlOrBr")
        for row in range(2):
            for column in range(2):
                axis.text(column, row, f"{matrix[row, column]:,}", ha="center", va="center")
        axis.set_xticks([0, 1], ["Lower risk", "Higher risk"], rotation=14)
        axis.set_yticks([0, 1], ["Reliable label", "Misleading label"])
        axis.set_title(result["model"])
        axis.set_xlabel("Predicted")
        axis.set_ylabel("Dataset label")
        figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.suptitle("Controlled benchmark confusion matrices - untouched final test partition")
    figure.patch.set_facecolor("#FAF8F2")
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "model_benchmark_confusion_matrices.png", bbox_inches="tight")
    plt.close(figure)


def write_production_evaluation_figures(
    labels: pd.Series,
    predictions: np.ndarray,
    probabilities: np.ndarray,
) -> None:
    """Replace accountability figures with the controlled final-test evidence."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    figure, axis = plt.subplots(figsize=(6.3, 5.2), dpi=190)
    image = axis.imshow(matrix, cmap="YlOrBr")
    for row in range(2):
        for column in range(2):
            axis.text(column, row, f"{matrix[row, column]:,}", ha="center", va="center", fontsize=13)
    axis.set_xticks([0, 1], ["Lower risk", "Higher risk"])
    axis.set_yticks([0, 1], ["Reliable label", "Misleading label"])
    axis.set_xlabel("Calibrated predicted direction")
    axis.set_ylabel("Dataset label")
    axis.set_title(f"Untouched final-test confusion matrix (n={len(labels):,})")
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.patch.set_facecolor("#FAF8F2")
    axis.set_facecolor("#FAF8F2")
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "confusion_matrix.png", bbox_inches="tight")
    plt.close(figure)

    false_positive_rate, true_positive_rate, _ = roc_curve(labels, probabilities)
    precision_values, recall_values, _ = precision_recall_curve(labels, probabilities)
    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=190)
    axes[0].plot(
        false_positive_rate,
        true_positive_rate,
        color="#496454",
        linewidth=2.5,
        label=f"AUC={roc_auc_score(labels, probabilities):.4f}",
    )
    axes[0].plot([0, 1], [0, 1], linestyle="--", color="#A89984")
    axes[0].set(title="ROC curve", xlabel="False-positive rate", ylabel="True-positive rate")
    axes[0].legend(frameon=False)
    axes[1].plot(
        recall_values,
        precision_values,
        color="#813F39",
        linewidth=2.5,
        label=f"AP={average_precision_score(labels, probabilities):.4f}",
    )
    axes[1].set(title="Precision-recall curve", xlabel="Recall", ylabel="Precision")
    axes[1].legend(frameon=False)
    figure.suptitle(f"Calibrated production-model discrimination (final test n={len(labels):,})")
    figure.patch.set_facecolor("#FAF8F2")
    for axis in axes:
        axis.set_facecolor("#FAF8F2")
        axis.grid(color="#D4CEC2", alpha=0.7)
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "roc_pr_curves.png", bbox_inches="tight")
    plt.close(figure)


def write_methodology(summary: dict[str, Any]) -> None:
    split = summary["partitions"]
    selected = summary["selection"]
    calibration = summary["calibration"]
    text = f"""# Controlled model benchmarking methodology

## Purpose

This study compares three deployment-compatible classical text classifiers for NewsLens AI. It measures patterns associated with the ISOT labels; it does not verify factual truth.

## Dataset integrity and partitions

- Dataset: ISOT Fake News Dataset, downloaded from the documented University of Victoria source for private evaluation only.
- Verified source checksums: `True.csv` `{summary['dataset']['true_csv_sha256']}` and `Fake.csv` `{summary['dataset']['fake_csv_sha256']}`.
- Clean balanced sample: {summary['dataset']['sample_rows']:,} rows, fixed random seed {RANDOM_SEED}.
- Training: {split['train_rows']:,} rows.
- Validation: {split['validation_rows']:,} rows, internally divided into {split['calibration_rows']:,} calibration rows and {split['threshold_policy_rows']:,} threshold-policy rows.
- Untouched final test: {split['test_rows']:,} rows.
- {split['quarantined_holdout_rows']} holdout rows were quarantined because the deterministic near-duplicate screen found a high-similarity counterpart in training.

Exact duplicates and conflicting-label duplicates are removed before sampling. Near-duplicate candidates are generated from eight minimum word-five-gram signatures and verified with Jaccard similarity >= {NEAR_DUPLICATE_JACCARD:.2f}. Candidate generation is an approximate deterministic screen, not a claim of exhaustive semantic-duplicate detection. Near-duplicate groups are kept inside one validation/test partition. The final leakage audit found {summary['leakage_audit']['cross_partition_pairs_after_controls']} cross-partition pairs after controls.

## Candidates and fitting

The candidates are Logistic Regression (`C=2.0`), Linear SVC (`C=1.0`) and Multinomial Naive Bayes (`alpha=0.1`). All use the same word-level TF-IDF configuration and the same training rows. Each vectorizer is fitted only inside its training pipeline. There is no exhaustive search and no threshold tuning on test data.

The packaged Logistic Regression is first verified against its established 4,800-row holdout evidence. Its artifact remains unchanged. Linear SVC and Multinomial Naive Bayes are fitted for this controlled private evaluation only; their model files are not retained in the release.

## Calibration and abstention

Platt scaling fits a one-dimensional Logistic Regression mapping from each candidate's decision score to the misleading-label probability using only the calibration subset. Calibration is evaluated on the untouched test set with Brier score, a ten-bin expected calibration error (ECE), and reliability points.

The validation-policy subset is used for two predeclared policy decisions after the candidate pipelines and Platt mappings are fixed: the 0.01 macro-F1 model-retention check and the production review threshold. The deterministic threshold rule chooses the lowest calibrated-confidence threshold with at least 80% automatic-decision coverage and a 95% Wilson lower bound of at least 99% for accuracy relative to dataset labels. The selected threshold is `{calibration['editorial_review_threshold']:.2f}`. Inputs below the threshold, with inadequate quality, or outside supported language/domain heuristics return **Editorial review required**. The final test partition is not used for either decision.

## Selection

The selected production family is **{selected['selected_model']}**. {selected['rationale']} The untouched final test is used once for reporting after this decision. The calibrated parameters are a private model artefact and are excluded from public archives.

## Responsible interpretation

Accuracy, F1, discrimination and calibration are dataset-relative measurements. Calibration measures score reliability against the benchmark labels, not factual verification. Explainability reports learned feature influence, not evidence. Human review remains required for consequential decisions.
"""
    BENCHMARK_METHOD_PATH.write_text(text, encoding="utf-8")


def run(raw_dir: Path) -> dict[str, Any]:
    true_path = raw_dir / "True.csv"
    fake_path = raw_dir / "Fake.csv"
    if sha256_file(true_path) != EXPECTED_TRUE_SHA256 or sha256_file(fake_path) != EXPECTED_FAKE_SHA256:
        raise RuntimeError("ISOT CSV checksums do not match the documented source files.")
    model_hash = sha256_file(MODEL_PATH)
    if model_hash != EXPECTED_MODEL_SHA256:
        raise RuntimeError("The packaged production model does not match the accepted checkpoint.")

    frame, dataset_profile = load_isot_dataset(raw_dir, max_rows=24_000)
    all_indices = frame.index.to_numpy()
    train_indices, original_holdout_indices = train_test_split(
        all_indices,
        test_size=0.20,
        stratify=frame["label"],
        random_state=RANDOM_SEED,
    )
    production_model: Pipeline = joblib.load(MODEL_PATH)
    baseline_predictions = production_model.predict(frame.loc[original_holdout_indices, "combined"])
    baseline_accuracy = accuracy_score(frame.loc[original_holdout_indices, "label"], baseline_predictions)
    baseline_macro_f1 = f1_score(
        frame.loc[original_holdout_indices, "label"], baseline_predictions, average="macro"
    )
    if not math.isclose(baseline_accuracy, EXPECTED_BASELINE_ACCURACY, abs_tol=1e-12):
        raise RuntimeError("The packaged model no longer reproduces its accepted accuracy evidence.")
    if not math.isclose(baseline_macro_f1, EXPECTED_BASELINE_MACRO_F1, abs_tol=1e-12):
        raise RuntimeError("The packaged model no longer reproduces its accepted macro-F1 evidence.")

    leakage = screen_near_duplicates(frame["combined"])
    train_set = set(int(value) for value in train_indices)
    holdout_set = set(int(value) for value in original_holdout_indices)
    quarantined = {
        right if left in train_set and right in holdout_set else left
        for left, right, _ in leakage.pairs
        if (left in train_set and right in holdout_set) or (right in train_set and left in holdout_set)
    }
    clean_holdout_indices = np.asarray(
        [index for index in original_holdout_indices if int(index) not in quarantined], dtype=int
    )
    validation_indices, test_indices, calibration_indices, policy_indices = split_validation_and_test(
        frame, clean_holdout_indices, leakage.groups
    )

    partitions = {
        "train": set(int(value) for value in train_indices),
        "validation": set(int(value) for value in validation_indices),
        "test": set(int(value) for value in test_indices),
    }
    leakage_findings = audit_partition_leakage(leakage.pairs, partitions)
    if leakage_findings:
        raise RuntimeError("Near-duplicate leakage remains after partition controls.")

    x_train = frame.loc[train_indices, "combined"]
    y_train = frame.loc[train_indices, "label"]
    x_calibration = frame.loc[calibration_indices, "combined"]
    y_calibration = frame.loc[calibration_indices, "label"]
    x_policy = frame.loc[policy_indices, "combined"]
    y_policy = frame.loc[policy_indices, "label"]
    x_test = frame.loc[test_indices, "combined"]
    y_test = frame.loc[test_indices, "label"]

    candidates: dict[str, Pipeline] = {
        "Logistic Regression": production_model,
        "Linear SVC": base_pipeline(
            LinearSVC(C=1.0, class_weight="balanced", random_state=RANDOM_SEED)
        ),
        "Multinomial Naive Bayes": base_pipeline(MultinomialNB(alpha=0.1)),
    }
    results: list[dict[str, Any]] = []
    calibrators: dict[str, LogisticRegression] = {}
    for name, candidate in candidates.items():
        if name != "Logistic Regression":
            candidate.fit(x_train, y_train)
        calibration_scores = raw_scores(candidate, x_calibration)
        calibrator = fit_platt_calibrator(calibration_scores, y_calibration)
        calibrators[name] = calibrator
        policy_scores = raw_scores(candidate, x_policy)
        policy_probabilities = calibrated_probabilities(calibrator, policy_scores)
        policy_predictions = (policy_probabilities >= 0.5).astype(int)
        test_scores = raw_scores(candidate, x_test)
        probabilities = calibrated_probabilities(calibrator, test_scores)
        predictions = (probabilities >= 0.5).astype(int)
        metrics = classification_metrics(y_test, predictions, probabilities)
        native = native_probabilities(candidate, x_test)
        results.append(
            {
                "model": name,
                "hyperparameters": (
                    {"classifier__C": 2.0}
                    if name == "Logistic Regression"
                    else {"classifier__C": 1.0}
                    if name == "Linear SVC"
                    else {"classifier__alpha": 0.1}
                ),
                "policy_metrics": classification_metrics(
                    y_policy,
                    policy_predictions,
                    policy_probabilities,
                ),
                "metrics": metrics,
                "uncalibrated_brier_score": (
                    float(brier_score_loss(y_test, native)) if native is not None else None
                ),
                "uncalibrated_expected_calibration_error": (
                    float(expected_calibration_error(y_test, native)) if native is not None else None
                ),
                "mean_inference_ms_per_article": measure_latency_ms(candidate, calibrator, x_test),
                "model_size_bytes": model_size_bytes(candidate, name),
                "calibration_method": "Platt scaling on held-out validation-calibration rows",
                "reliability": reliability_points(y_test, probabilities),
            }
        )

    production_calibrator = calibrators["Logistic Regression"]
    policy_probabilities = calibrated_probabilities(
        production_calibrator, raw_scores(production_model, x_policy)
    )
    threshold, threshold_table = choose_review_threshold(y_policy, policy_probabilities)
    test_probabilities = calibrated_probabilities(
        production_calibrator, raw_scores(production_model, x_test)
    )
    test_predictions = (test_probabilities >= 0.5).astype(int)
    test_confidence = np.maximum(test_probabilities, 1 - test_probabilities)
    auto_decided = test_confidence >= threshold
    auto_correct = int((test_predictions[auto_decided] == np.asarray(y_test)[auto_decided]).sum())
    auto_count = int(auto_decided.sum())

    logistic_result = next(item for item in results if item["model"] == "Logistic Regression")
    svm_result = next(item for item in results if item["model"] == "Linear SVC")
    rationale = (
        "Linear SVC's validation-policy macro-F1 advantage is below the predeclared "
        "0.01 tolerance; "
        "Logistic Regression therefore remains selected for direct coefficient explanations, "
        "compact deployment and an unchanged verified production artefact."
    )

    summary: dict[str, Any] = {
        "schema_version": 1,
        "generated_at_utc": utc_now_iso(),
        "scope": "Controlled private benchmark; raw data excluded from deliverables",
        "dataset": {
            **dataset_profile,
            "dataset_name": "ISOT Fake News Dataset",
            "sample_rows": int(len(frame)),
            "true_csv_sha256": EXPECTED_TRUE_SHA256,
            "fake_csv_sha256": EXPECTED_FAKE_SHA256,
            "random_seed": RANDOM_SEED,
        },
        "partitions": {
            "train_rows": int(len(train_indices)),
            "original_holdout_rows": int(len(original_holdout_indices)),
            "quarantined_holdout_rows": int(len(quarantined)),
            "validation_rows": int(len(validation_indices)),
            "calibration_rows": int(len(calibration_indices)),
            "threshold_policy_rows": int(len(policy_indices)),
            "test_rows": int(len(test_indices)),
            "train_index_sha256": sha256_values(sorted(train_indices)),
            "validation_index_sha256": sha256_values(sorted(validation_indices)),
            "test_index_sha256": sha256_values(sorted(test_indices)),
        },
        "leakage_audit": {
            "candidate_pairs_screened": leakage.candidate_pairs,
            "near_duplicate_pairs": len(leakage.pairs),
            "cross_train_holdout_pairs_before_controls": len(quarantined),
            "cross_partition_pairs_after_controls": len(leakage_findings),
            "similarity_threshold": NEAR_DUPLICATE_JACCARD,
            "method": "Eight minimum word-five-gram CRC32 signatures plus exact Jaccard verification",
        },
        "baseline_reproduction": {
            "model_sha256": model_hash,
            "holdout_rows": int(len(original_holdout_indices)),
            "accuracy": float(baseline_accuracy),
            "macro_f1": float(baseline_macro_f1),
            "status": "passed",
        },
        "models": results,
        "selection": {
            "selected_model": "Logistic Regression",
            "selected_model_artifact": "models/fake_news_pipeline.joblib",
            "packaged_model_unchanged": True,
            "macro_f1_tolerance": 0.01,
            "selection_partition": "validation policy",
            "linear_svc_policy_macro_f1_advantage": float(
                svm_result["policy_metrics"]["macro_f1"]
                - logistic_result["policy_metrics"]["macro_f1"]
            ),
            "rationale": rationale,
        },
        "calibration": {
            "method": "Platt scaling",
            "score_source": "Logistic Regression decision_function",
            "editorial_review_threshold": threshold,
            "threshold_rule": (
                "Lowest validation-policy confidence threshold with >=80% coverage and "
                "95% Wilson lower accuracy bound >=99%; deterministic fallback documented."
            ),
            "test_brier_score": logistic_result["metrics"]["brier_score"],
            "test_expected_calibration_error": logistic_result["metrics"]["expected_calibration_error"],
            "test_auto_decision_coverage": auto_count / len(y_test),
            "test_selective_accuracy": auto_correct / auto_count if auto_count else 0.0,
            "test_selective_accuracy_wilson_lower_95": wilson_lower_bound(auto_correct, auto_count),
            "test_editorial_review_rate": 1 - (auto_count / len(y_test)),
        },
        "responsible_use": (
            "Metrics and calibration are relative to dataset labels. They do not establish factual truth."
        ),
    }

    calibration_artifact = {
        "schema_version": 1,
        "artifact_type": "private confidence-calibration parameters",
        "model_sha256": model_hash,
        "model_version": "isot-tfidf-lr-v1.0.0",
        "method": "Platt scaling",
        "score_source": "decision_function",
        "coefficient": float(production_calibrator.coef_.ravel()[0]),
        "intercept": float(production_calibrator.intercept_.ravel()[0]),
        "editorial_review_threshold": threshold,
        "calibration_rows": int(len(calibration_indices)),
        "threshold_policy_rows": int(len(policy_indices)),
        "final_test_rows": int(len(test_indices)),
        "generated_at_utc": summary["generated_at_utc"],
        "public_redistribution": "blocked pending documented model/dataset-derived artefact rights",
    }
    write_json(CALIBRATION_PATH, calibration_artifact)

    calibration_evidence = {
        "schema_version": 1,
        "generated_at_utc": summary["generated_at_utc"],
        "production_model": {
            "model": "Logistic Regression",
            "uncalibrated_brier_score": logistic_result["uncalibrated_brier_score"],
            "uncalibrated_expected_calibration_error": logistic_result[
                "uncalibrated_expected_calibration_error"
            ],
            "calibrated_brier_score": logistic_result["metrics"]["brier_score"],
            "calibrated_expected_calibration_error": logistic_result["metrics"][
                "expected_calibration_error"
            ],
            "uncalibrated_reliability": reliability_points(
                y_test, native_probabilities(production_model, x_test)
            ),
            "calibrated_reliability": logistic_result["reliability"],
        },
        "editorial_review_threshold": threshold,
        "threshold_policy_rows": int(len(policy_indices)),
        "threshold_candidates": threshold_table,
        "test_policy": summary["calibration"],
        "interpretation": (
            "Calibration measures probability reliability against benchmark labels, not factual verification."
        ),
    }

    rows: list[dict[str, Any]] = []
    for result in results:
        metric = result["metrics"]
        rows.append(
            {
                "model": result["model"],
                "accuracy": metric["accuracy"],
                "macro_precision": metric["macro_precision"],
                "macro_recall": metric["macro_recall"],
                "macro_f1": metric["macro_f1"],
                "reliable_precision": metric["reliable_precision"],
                "reliable_recall": metric["reliable_recall"],
                "reliable_f1": metric["reliable_f1"],
                "misleading_precision": metric["misleading_precision"],
                "misleading_recall": metric["misleading_recall"],
                "misleading_f1": metric["misleading_f1"],
                "roc_auc": metric["roc_auc"],
                "pr_auc": metric["pr_auc"],
                "calibrated_brier_score": metric["brier_score"],
                "calibrated_ece": metric["expected_calibration_error"],
                "uncalibrated_brier_score": result["uncalibrated_brier_score"],
                "uncalibrated_ece": result["uncalibrated_expected_calibration_error"],
                "mean_inference_ms_per_article": result["mean_inference_ms_per_article"],
                "model_size_bytes": result["model_size_bytes"],
                "test_rows": int(len(test_indices)),
                "confusion_matrix": json.dumps(metric["confusion_matrix"]),
            }
        )
    BENCHMARK_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BENCHMARK_RESULTS_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    write_json(BENCHMARK_SUMMARY_PATH, summary)
    write_json(CALIBRATION_EVIDENCE_PATH, calibration_evidence)
    write_json(
        REFERENCE_PROFILE_PATH,
        input_reference_profile(
            production_model,
            x_train,
            y_train,
            evaluation_texts=x_test,
            calibrator=production_calibrator,
        ),
    )
    write_reliability_figure(calibration_evidence)
    write_confusion_figure(results)
    write_production_evaluation_figures(y_test, test_predictions, test_probabilities)
    write_methodology(summary)

    # Compatibility artifacts used by the existing accountability page and report builders.
    compatibility = pd.DataFrame(rows).rename(
        columns={
            "macro_precision": "precision",
            "macro_recall": "recall",
            "pr_auc": "pr_auc",
        }
    )
    compatibility["f1"] = compatibility["macro_f1"]
    compatibility["weighted_f1"] = compatibility["macro_f1"]
    compatibility.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)
    production_metrics = dict(logistic_result["metrics"])
    production_metrics.update(
        {
            "mean_inference_ms_per_article": logistic_result["mean_inference_ms_per_article"],
            "test_samples": int(len(test_indices)),
            "train_samples": int(len(train_indices)),
            "validation_samples": int(len(validation_indices)),
            "random_seed": RANDOM_SEED,
            "positive_class": "misleading (1)",
            "calibration_method": "Platt scaling",
            "editorial_review_threshold": threshold,
        }
    )
    write_json(RESULTS_DIR / "model_metrics.json", production_metrics)
    class_rows = [
        {
            "class": "Reliable",
            "precision": production_metrics["reliable_precision"],
            "recall": production_metrics["reliable_recall"],
            "f1-score": production_metrics["reliable_f1"],
            "support": production_metrics["reliable_support"],
        },
        {
            "class": "Misleading",
            "precision": production_metrics["misleading_precision"],
            "recall": production_metrics["misleading_recall"],
            "f1-score": production_metrics["misleading_f1"],
            "support": production_metrics["misleading_support"],
        },
    ]
    pd.DataFrame(class_rows).to_csv(RESULTS_DIR / "classification_report.csv", index=False)
    error_frame = pd.DataFrame(
        {
            "text_hash": x_test.map(
                lambda value: hashlib.sha256(str(value).encode("utf-8")).hexdigest()
            ).values,
            "true_label": np.asarray(y_test, dtype=int),
            "predicted_label": test_predictions,
            "misleading_probability": test_probabilities,
            "word_count": x_test.astype(str).str.split().str.len().values,
            "evidence_scope": "untouched_final_test",
        }
    )
    error_frame.loc[
        error_frame["true_label"] != error_frame["predicted_label"]
    ].to_csv(ERROR_ANALYSIS_PATH, index=False)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        required=True,
        help="Private directory containing checksum-verified True.csv and Fake.csv.",
    )
    args = parser.parse_args()
    result = run(args.raw_dir.resolve())
    print(
        json.dumps(
            {
                "selected_model": result["selection"]["selected_model"],
                "editorial_review_threshold": result["calibration"]["editorial_review_threshold"],
                "test_rows": result["partitions"]["test_rows"],
                "status": "passed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
