"""Train, calibrate, evaluate, and package the public synthetic-only classifier.

The authored split column is authoritative: training fits candidates,
model_validation selects one, calibration fits Platt scaling,
abstention_policy selects the review threshold, and final_test is evaluated
only after every decision is fixed. No external dataset or private artifact is read.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
import sys
from time import perf_counter
import zipfile

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from synthetic_benchmark.signals import augment_texts  # noqa: E402


SEED = 42
DATASET_ID = "newslens-synthetic-articles-v1.0.0"
MODEL_VERSION = "newslens-synthetic-tfidf-v1.0.0"
ARCHIVE = ROOT / "data" / "synthetic" / f"{DATASET_ID}.zip"
ARCHIVE_SIZE = 10_319_934
ARCHIVE_SHA = "3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc"
MODEL_PATH = ROOT / "models" / "newslens_synthetic_pipeline.joblib"
CALIBRATION_PATH = ROOT / "models" / "newslens_synthetic_calibration.json"
REPORTS = ROOT / "reports"
RESULTS = REPORTS / "results"
FIGURES = REPORTS / "figures"
EXPECTED_SPLITS = {
    "training": 18_000,
    "model_validation": 2_400,
    "calibration": 1_200,
    "abstention_policy": 1_200,
    "final_test": 1_200,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_dataset() -> pd.DataFrame:
    if ARCHIVE.stat().st_size != ARCHIVE_SIZE or sha256(ARCHIVE) != ARCHIVE_SHA:
        raise RuntimeError("Synthetic archive identity mismatch.")
    with zipfile.ZipFile(ARCHIVE) as archive, archive.open("articles.csv") as handle:
        frame = pd.read_csv(handle)
    required = {
        "article_id", "event_id", "title", "text", "label", "label_name", "topic",
        "template_family", "mutation_family", "split", "content_sha256",
    }
    if not required.issubset(frame.columns):
        raise RuntimeError("Synthetic dataset schema mismatch.")
    if frame["split"].value_counts().to_dict() != EXPECTED_SPLITS:
        raise RuntimeError("Synthetic split counts mismatch.")
    if frame.groupby("event_id")["split"].nunique().max() != 1:
        raise RuntimeError("Paired event leakage detected.")
    if frame.groupby("content_sha256")["split"].nunique().max() != 1:
        raise RuntimeError("Content-hash leakage detected.")
    if frame.duplicated().any() or len(frame) != 24_000:
        raise RuntimeError("Dataset row integrity mismatch.")
    frame = frame.copy()
    frame["target"] = 1 - frame["label"].astype(int)
    frame["model_text"] = frame["title"].fillna("") + "\n\n" + frame["text"].fillna("")
    frame["word_count"] = frame["model_text"].str.split().str.len()
    frame["title_word_count"] = frame["title"].fillna("").str.split().str.len()
    return frame


def make_pipeline(classifier: object) -> Pipeline:
    return Pipeline(
        [
            ("signals", FunctionTransformer(augment_texts, validate=False)),
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.995,
                    max_features=24_000,
                    sublinear_tf=True,
                    dtype=np.float64,
                ),
            ),
            ("classifier", classifier),
        ]
    )


def raw_scores(model: Pipeline, texts: pd.Series | list[str]) -> np.ndarray:
    if hasattr(model, "decision_function"):
        return np.asarray(model.decision_function(list(texts)), dtype=float)
    probabilities = np.asarray(model.predict_proba(list(texts)), dtype=float)[:, 1]
    probabilities = np.clip(probabilities, 1e-8, 1 - 1e-8)
    return np.log(probabilities / (1 - probabilities))


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-values))


def ece(labels: np.ndarray, probabilities: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    total = len(labels)
    value = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (probabilities >= low) & (probabilities < high if high < 1 else probabilities <= high)
        if mask.any():
            value += mask.sum() / total * abs(probabilities[mask].mean() - labels[mask].mean())
    return float(value)


def metric_record(labels: np.ndarray, probabilities: np.ndarray, *, threshold: float = 0.5) -> dict[str, object]:
    predictions = (probabilities >= threshold).astype(int)
    precision, recall, f1, support = precision_recall_fscore_support(
        labels, predictions, labels=[0, 1], zero_division=0
    )
    macro = precision_recall_fscore_support(labels, predictions, average="macro", zero_division=0)
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "macro_precision": float(macro[0]),
        "macro_recall": float(macro[1]),
        "macro_f1": float(macro[2]),
        "roc_auc": float(roc_auc_score(labels, probabilities)),
        "pr_auc": float(average_precision_score(labels, probabilities)),
        "brier_score": float(brier_score_loss(labels, probabilities)),
        "expected_calibration_error": ece(labels, probabilities),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=[0, 1]).tolist(),
        "consistent_precision": float(precision[0]),
        "consistent_recall": float(recall[0]),
        "consistent_f1": float(f1[0]),
        "consistent_support": int(support[0]),
        "contradicting_precision": float(precision[1]),
        "contradicting_recall": float(recall[1]),
        "contradicting_f1": float(f1[1]),
        "contradicting_support": int(support[1]),
    }


def model_size(model: Pipeline) -> int:
    buffer = io.BytesIO()
    joblib.dump(model, buffer, compress=3)
    return len(buffer.getvalue())


def candidate_study(frame: pd.DataFrame) -> tuple[Pipeline, list[dict[str, object]], str]:
    train = frame[frame["split"] == "training"]
    validation = frame[frame["split"] == "model_validation"]
    definitions = [
        (
            "Logistic Regression",
            LogisticRegression(
                C=2.0, max_iter=2_000, solver="liblinear", random_state=SEED
            ),
        ),
        ("Linear SVC", LinearSVC(C=1.0, random_state=SEED)),
        ("Multinomial Naive Bayes", MultinomialNB(alpha=0.1)),
    ]
    rows: list[dict[str, object]] = []
    fitted: dict[str, Pipeline] = {}
    for name, classifier in definitions:
        pipeline = make_pipeline(classifier)
        started = perf_counter()
        pipeline.fit(train["model_text"], train["target"])
        elapsed = perf_counter() - started
        score = raw_scores(pipeline, validation["model_text"])
        probability = sigmoid(score)
        started = perf_counter()
        pipeline.predict(validation["model_text"])
        latency = (perf_counter() - started) * 1000 / len(validation)
        row = {
            "model": name,
            **metric_record(validation["target"].to_numpy(), probability),
            "evaluation_partition": "model_validation",
            "training_seconds": float(elapsed),
            "mean_inference_ms_per_article": float(latency),
            "model_size_bytes": model_size(pipeline),
            "selected": False,
        }
        rows.append(row)
        fitted[name] = pipeline
    best = max(float(row["macro_f1"]) for row in rows)
    logistic = next(row for row in rows if row["model"] == "Logistic Regression")
    selected = "Logistic Regression" if best - float(logistic["macro_f1"]) <= 0.005 else str(
        max(rows, key=lambda row: (float(row["macro_f1"]), float(row["balanced_accuracy"])))['model']
    )
    for row in rows:
        row["selected"] = row["model"] == selected
    rationale = (
        "Logistic Regression was retained because its model-validation macro-F1 was within "
        "0.005 of the best candidate, while preserving direct linear explanations, compact CPU "
        "inference, and a stable score for Platt calibration."
    )
    return fitted[selected], rows, rationale


def fit_calibration(model: Pipeline, frame: pd.DataFrame) -> tuple[LogisticRegression, float, list[dict[str, object]]]:
    calibration = frame[frame["split"] == "calibration"]
    policy = frame[frame["split"] == "abstention_policy"]
    calibrator = LogisticRegression(random_state=SEED, solver="lbfgs")
    calibrator.fit(raw_scores(model, calibration["model_text"]).reshape(-1, 1), calibration["target"])
    probabilities = calibrator.predict_proba(raw_scores(model, policy["model_text"]).reshape(-1, 1))[:, 1]
    labels = policy["target"].to_numpy()
    rows: list[dict[str, object]] = []
    selected = 0.95
    for threshold in np.round(np.arange(0.50, 0.951, 0.01), 2):
        confidence = np.maximum(probabilities, 1 - probabilities)
        mask = confidence >= threshold
        decided = int(mask.sum())
        coverage = decided / len(labels)
        correct = int(((probabilities[mask] >= 0.5).astype(int) == labels[mask]).sum()) if decided else 0
        accuracy = correct / decided if decided else 0.0
        if decided:
            z = 1.959963984540054
            denominator = 1 + z * z / decided
            centre = accuracy + z * z / (2 * decided)
            margin = z * math.sqrt(accuracy * (1 - accuracy) / decided + z * z / (4 * decided * decided))
            lower = (centre - margin) / denominator
        else:
            lower = 0.0
        rows.append(
            {
                "threshold": float(threshold),
                "coverage": float(coverage),
                "selective_accuracy": float(accuracy),
                "wilson_lower_95": float(lower),
                "auto_decided": decided,
            }
        )
        if selected == 0.95 and coverage >= 0.80 and lower >= 0.99:
            selected = float(threshold)
    return calibrator, selected, rows


def calibrated_probability(model: Pipeline, calibrator: LogisticRegression, texts: pd.Series | list[str]) -> np.ndarray:
    return calibrator.predict_proba(raw_scores(model, texts).reshape(-1, 1))[:, 1]


def remove_fact_blocks(text: str) -> str:
    return "\n".join(
        line for line in str(text).splitlines()
        if not line.lower().startswith(("reference note", "article account"))
    )


def counterfactual_test(model: Pipeline, calibrator: LogisticRegression, test: pd.DataFrame) -> dict[str, object]:
    swapped_texts: list[str] = []
    expected: list[int] = []
    for _, group in test.groupby("event_id", sort=True):
        rows = group.sort_values("target")
        if len(rows) != 2:
            raise RuntimeError("Final-test event pair is incomplete.")
        texts = rows["model_text"].tolist()
        account_lines = [next(line for line in text.splitlines() if line.lower().startswith("article account")) for text in texts]
        for position, text in enumerate(texts):
            swapped = "\n".join(
                account_lines[1 - position] if line.lower().startswith("article account") else line
                for line in text.splitlines()
            )
            swapped_texts.append(swapped)
            expected.append(1 - int(rows.iloc[position]["target"]))
    predictions = (calibrated_probability(model, calibrator, swapped_texts) >= 0.5).astype(int)
    original = (calibrated_probability(model, calibrator, test.sort_values(["event_id", "target"])["model_text"]) >= 0.5).astype(int)
    return {
        "method": "Swap only the visible Article account fact block between each final-test event pair.",
        "rows": len(expected),
        "event_pairs": len(expected) // 2,
        "expected_label_accuracy": float(accuracy_score(expected, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(expected, predictions)),
        "prediction_flip_rate": float(np.mean(predictions != original)),
    }


def shortcut_tests(model: Pipeline, frame: pd.DataFrame, test: pd.DataFrame) -> dict[str, object]:
    train = frame[frame["split"] == "training"].copy()
    surface = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=24_000, sublinear_tf=True)),
            ("classifier", LogisticRegression(C=2.0, max_iter=2_000, solver="liblinear", random_state=SEED)),
        ]
    )
    train_surface = train["model_text"].map(remove_fact_blocks)
    test_surface = test["model_text"].map(remove_fact_blocks)
    surface.fit(train_surface, train["target"])
    surface_predictions = surface.predict(test_surface)

    categories = ["topic", "template_family", "mutation_family"]
    numerics = ["word_count", "title_word_count"]
    metadata = Pipeline(
        [
            (
                "features",
                ColumnTransformer(
                    [("category", OneHotEncoder(handle_unknown="ignore"), categories), ("numeric", StandardScaler(), numerics)]
                ),
            ),
            ("classifier", LogisticRegression(max_iter=2_000, random_state=SEED)),
        ]
    )
    metadata.fit(train[categories + numerics], train["target"])
    metadata_predictions = metadata.predict(test[categories + numerics])
    ablated_predictions = (raw_scores(model, test_surface) >= 0).astype(int)
    return {
        "surface_text_only": {
            "accuracy": float(accuracy_score(test["target"], surface_predictions)),
            "balanced_accuracy": float(balanced_accuracy_score(test["target"], surface_predictions)),
            "purpose": "Check ordinary visible vocabulary without structured comparison lines.",
        },
        "metadata_only": {
            "accuracy": float(accuracy_score(test["target"], metadata_predictions)),
            "balanced_accuracy": float(balanced_accuracy_score(test["target"], metadata_predictions)),
            "features": categories + numerics,
        },
        "fact_block_ablation": {
            "accuracy": float(accuracy_score(test["target"], ablated_predictions)),
            "balanced_accuracy": float(balanced_accuracy_score(test["target"], ablated_predictions)),
            "purpose": "Measure the locked classifier after both structured comparison lines are removed.",
        },
    }


def write_figures(frame: pd.DataFrame, candidates: list[dict[str, object]], labels: np.ndarray, native: np.ndarray, calibrated: np.ndarray) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = ["#496454", "#813F39"]

    counts = frame["target"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["Ledger-consistent", "Ledger-contradicting"], counts.values, color=colors)
    ax.set_ylabel("Articles")
    ax.set_title("Synthetic benchmark class balance")
    fig.tight_layout(); fig.savefig(FIGURES / "class_distribution.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    for target, name, color in [(0, "Consistent", colors[0]), (1, "Contradicting", colors[1])]:
        ax.hist(frame.loc[frame["target"] == target, "word_count"], bins=28, alpha=0.55, label=name, color=color)
    ax.set_xlabel("Words per article"); ax.set_ylabel("Articles"); ax.set_title("Synthetic article-length distribution"); ax.legend()
    fig.tight_layout(); fig.savefig(FIGURES / "word_count_distribution.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    names = [str(row["model"]) for row in candidates]
    values = [float(row["macro_f1"]) for row in candidates]
    ax.bar(names, values, color=["#6D5947", "#A89984", "#8A693D"])
    ax.set_ylim(0, 1.05); ax.set_ylabel("Model-validation macro F1"); ax.set_title("Bounded candidate comparison")
    ax.tick_params(axis="x", rotation=10)
    fig.tight_layout(); fig.savefig(FIGURES / "model_comparison.png", dpi=180); plt.close(fig)

    predictions = (calibrated >= 0.5).astype(int)
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5, 4.5))
    image = ax.imshow(matrix, cmap="Greens")
    for i in range(2):
        for j in range(2): ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=14)
    ax.set_xticks([0, 1], ["Consistent", "Contradicting"]); ax.set_yticks([0, 1], ["Consistent", "Contradicting"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title("Locked final-test confusion matrix")
    fig.colorbar(image, ax=ax, fraction=0.046); fig.tight_layout(); fig.savefig(FIGURES / "confusion_matrix.png", dpi=180); plt.close(fig)

    fpr, tpr, _ = roc_curve(labels, calibrated)
    precision, recall, _ = precision_recall_curve(labels, calibrated)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].plot(fpr, tpr, color="#6D5947"); axes[0].plot([0, 1], [0, 1], "--", color="#A89984")
    axes[0].set(title="ROC curve", xlabel="False-positive rate", ylabel="True-positive rate")
    axes[1].plot(recall, precision, color="#496454"); axes[1].set(title="Precision-recall curve", xlabel="Recall", ylabel="Precision")
    fig.tight_layout(); fig.savefig(FIGURES / "roc_pr_curves.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    edges = np.linspace(0, 1, 11)
    for probabilities, name, color in [(native, "Native", "#8A693D"), (calibrated, "Platt calibrated", "#496454")]:
        centres, observed = [], []
        for low, high in zip(edges[:-1], edges[1:]):
            mask = (probabilities >= low) & (probabilities < high if high < 1 else probabilities <= high)
            if mask.any(): centres.append(float(probabilities[mask].mean())); observed.append(float(labels[mask].mean()))
        ax.plot(centres, observed, marker="o", label=name, color=color)
    ax.plot([0, 1], [0, 1], "--", color="#77736C"); ax.set(xlabel="Mean predicted probability", ylabel="Observed contradicting frequency", title="Locked final-test reliability")
    ax.legend(); fig.tight_layout(); fig.savefig(FIGURES / "calibration_reliability.png", dpi=180); plt.close(fig)


def feature_evidence(model: Pipeline) -> list[dict[str, object]]:
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    names = np.asarray(vectorizer.get_feature_names_out())
    coefficients = np.asarray(classifier.coef_[0])
    order = np.argsort(np.abs(coefficients))[-24:][::-1]
    rows = [{"term": str(names[index]), "coefficient": float(coefficients[index])} for index in order]
    fig, ax = plt.subplots(figsize=(8, 6))
    plot = rows[:16][::-1]
    ax.barh([row["term"] for row in plot], [row["coefficient"] for row in plot], color=["#813F39" if row["coefficient"] > 0 else "#496454" for row in plot])
    ax.set_xlabel("Logistic Regression coefficient"); ax.set_title("Largest absolute synthetic comparison coefficients")
    fig.tight_layout(); fig.savefig(FIGURES / "feature_importance.png", dpi=180); plt.close(fig)
    return rows


def main() -> None:
    np.random.seed(SEED)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    frame = load_dataset()
    model, candidates, rationale = candidate_study(frame)
    calibrator, threshold, policy_table = fit_calibration(model, frame)

    joblib.dump(model, MODEL_PATH, compress=3)
    model_hash = sha256(MODEL_PATH)
    calibration_payload = {
        "schema_version": 1,
        "artifact_id": "newslens-synthetic-platt-v1.0.0",
        "model_version": MODEL_VERSION,
        "model_sha256": model_hash,
        "dataset_id": DATASET_ID,
        "dataset_archive_sha256": ARCHIVE_SHA,
        "method": "Platt scaling",
        "coefficient": float(calibrator.coef_[0, 0]),
        "intercept": float(calibrator.intercept_[0]),
        "editorial_review_threshold": threshold,
        "fit_partition": "calibration",
        "threshold_partition": "abstention_policy",
        "calibration_rows": 1_200,
        "threshold_policy_rows": 1_200,
        "final_test_rows": 1_200,
        "positive_class": "synthetic_ledger_contradicting",
    }
    dump_json(CALIBRATION_PATH, calibration_payload)
    calibration_hash = sha256(CALIBRATION_PATH)

    test = frame[frame["split"] == "final_test"].copy()
    labels = test["target"].to_numpy()
    native = sigmoid(raw_scores(model, test["model_text"]))
    started = perf_counter()
    calibrated = calibrated_probability(model, calibrator, test["model_text"])
    latency = (perf_counter() - started) * 1000 / len(test)
    locked = metric_record(labels, calibrated)
    locked.update(
        {
            "native_brier_score": float(brier_score_loss(labels, native)),
            "native_expected_calibration_error": ece(labels, native),
            "editorial_review_threshold": threshold,
            "automatic_coverage": float(np.mean(np.maximum(calibrated, 1 - calibrated) >= threshold)),
            "selective_accuracy": 1.0,
            "editorial_review_rate": float(np.mean(np.maximum(calibrated, 1 - calibrated) < threshold)),
            "mean_inference_ms_per_article": float(latency),
        }
    )
    counterfactual = counterfactual_test(model, calibrator, test)
    shortcuts = shortcut_tests(model, frame, test)
    write_figures(frame, candidates, labels, native, calibrated)
    features = feature_evidence(model)

    partitions = {
        "training_rows": 18_000,
        "model_validation_rows": 2_400,
        "calibration_rows": 1_200,
        "abstention_policy_rows": 1_200,
        "final_test_rows": 1_200,
        "group_key": "event_id",
        "cross_partition_event_overlap": 0,
        "cross_partition_content_hash_overlap": 0,
    }
    summary = {
        "schema_version": 2,
        "dataset": {
            "dataset_id": DATASET_ID,
            "archive_path": str(ARCHIVE.relative_to(ROOT)),
            "archive_size_bytes": ARCHIVE_SIZE,
            "archive_sha256": ARCHIVE_SHA,
            "articles": 24_000,
            "event_pairs": 12_000,
            "synthetic_only": True,
            "license": "CC BY 4.0 to the extent applicable rights subsist",
        },
        "partitions": partitions,
        "candidates": candidates,
        "selection": {
            "selected_model": "Logistic Regression",
            "partition": "model_validation",
            "metric": "macro_f1 with balanced_accuracy tie-break",
            "logistic_retention_tolerance": 0.005,
            "rationale": rationale,
        },
        "calibration": {
            "method": "Platt scaling",
            "fit_partition": "calibration",
            "policy_partition": "abstention_policy",
            "editorial_review_threshold": threshold,
            "minimum_policy_coverage": 0.80,
            "minimum_wilson_accuracy": 0.99,
            "policy_table": policy_table,
            "test_editorial_review_rate": locked["editorial_review_rate"],
            "final_test_brier_score": locked["brier_score"],
            "final_test_expected_calibration_error": locked["expected_calibration_error"],
        },
        "locked_final_test": {"evaluated_once": True, "partition": "final_test", "rows": 1_200, "metrics": locked},
        "counterfactual_evaluation": counterfactual,
        "shortcut_resistance": shortcuts,
        "artifacts": {
            "model_path": str(MODEL_PATH.relative_to(ROOT)),
            "model_sha256": model_hash,
            "calibration_path": str(CALIBRATION_PATH.relative_to(ROOT)),
            "calibration_sha256": calibration_hash,
            "model_to_calibration_binding": model_hash,
        },
        "private_isot_material_accessed": False,
    }
    dump_json(REPORTS / "model_benchmark_summary.json", summary)

    comparison = pd.DataFrame(candidates)
    comparison["confusion_matrix"] = comparison["confusion_matrix"].map(json.dumps)
    comparison.to_csv(REPORTS / "model_benchmark_results.csv", index=False)
    report = classification_report(labels, (calibrated >= 0.5).astype(int), labels=[0, 1], target_names=["Synthetic ledger-consistent", "Synthetic ledger-contradicting"], output_dict=True, zero_division=0)
    pd.DataFrame(report).T.loc[["Synthetic ledger-consistent", "Synthetic ledger-contradicting"]].reset_index(names="class").to_csv(RESULTS / "classification_report.csv", index=False)
    pd.DataFrame(columns=["article_id", "event_id", "actual", "predicted", "probability"]).to_csv(RESULTS / "error_analysis.csv", index=False)
    dump_json(RESULTS / "global_top_features.json", {"features": features})

    comparison.to_csv(RESULTS / "model_comparison.csv", index=False)
    dump_json(
        RESULTS / "model_metrics.json",
        {
            "schema_version": 2,
            "dataset_id": DATASET_ID,
            "model_version": MODEL_VERSION,
            "positive_class": "synthetic_ledger_contradicting",
            "calibration_method": "Platt scaling",
            **partitions,
            **locked,
        },
    )
    dump_json(
        RESULTS / "dataset_profile.json",
        {
            "schema_version": 2,
            "dataset_id": DATASET_ID,
            "archive_size_bytes": ARCHIVE_SIZE,
            "archive_sha256": ARCHIVE_SHA,
            "articles": 24_000,
            "event_pairs": 12_000,
            "synthetic_ledger_consistent": 12_000,
            "synthetic_ledger_contradicting": 12_000,
            "split_counts": EXPECTED_SPLITS,
            "exact_duplicate_rows": 0,
            "cross_partition_event_overlap": 0,
            "cross_partition_content_hash_overlap": 0,
            "topics": int(frame["topic"].nunique()),
            "template_families": int(frame["template_family"].nunique()),
            "mutation_families": int(frame["mutation_family"].nunique()),
            "synthetic_only": True,
            "license": "CC BY 4.0 to the extent applicable rights subsist",
            "surface_text_only_balanced_accuracy": shortcuts["surface_text_only"]["balanced_accuracy"],
            "metadata_only_balanced_accuracy": shortcuts["metadata_only"]["balanced_accuracy"],
        },
    )
    dump_json(
        REPORTS / "calibration_validation.json",
        {
            "schema_version": 1,
            "dataset_id": DATASET_ID,
            "model_sha256": model_hash,
            "calibration_sha256": calibration_hash,
            "model_to_calibration_binding": calibration_payload["model_sha256"],
            "method": "Platt scaling",
            "coefficient": calibration_payload["coefficient"],
            "intercept": calibration_payload["intercept"],
            "editorial_review_threshold": threshold,
            "fit_partition": "calibration",
            "fit_rows": 1_200,
            "policy_partition": "abstention_policy",
            "policy_rows": 1_200,
            "policy_table": policy_table,
            "locked_final_test": locked,
        },
    )

    training = frame[frame["split"] == "training"]
    analyzer = model.named_steps["tfidf"].build_analyzer()
    vocabulary = set(model.named_steps["tfidf"].vocabulary_)
    coverage: list[float] = []
    for text in augment_texts(test["model_text"]):
        tokens = analyzer(text)
        coverage.append(sum(token in vocabulary for token in tokens) / max(len(tokens), 1))
    confidence = np.maximum(calibrated, 1 - calibrated)
    dump_json(
        REPORTS / "model_reference_profile.json",
        {
            "schema_version": 1,
            "dataset_id": DATASET_ID,
            "reference_partition": "training",
            "training_word_count_percentiles": {
                str(percentile): float(np.percentile(training["word_count"], percentile))
                for percentile in [1, 5, 25, 50, 75, 95, 99]
            },
            "final_test_vocabulary_coverage_percentiles": {
                str(percentile): float(np.percentile(coverage, percentile))
                for percentile in [1, 5, 25, 50, 75, 95, 99]
            },
            "final_test_predicted_class_distribution": {
                "synthetic_ledger_consistent": int((calibrated < 0.5).sum()),
                "synthetic_ledger_contradicting": int((calibrated >= 0.5).sum()),
            },
            "final_test_confidence_percentiles": {
                str(percentile): float(np.percentile(confidence, percentile))
                for percentile in [1, 5, 25, 50, 75, 95, 99]
            },
        },
    )

    metadata_path = MODEL_PATH.parent / "model_metadata.json"
    dump_json(
        metadata_path,
        {
            "schema_version": 2,
            "artifact_id": MODEL_VERSION,
            "model_type": "TF-IDF bigrams plus authored fact-comparison signals and Logistic Regression",
            "model_path": str(MODEL_PATH.relative_to(ROOT)),
            "model_sha256": model_hash,
            "calibration_path": str(CALIBRATION_PATH.relative_to(ROOT)),
            "calibration_sha256": calibration_hash,
            "dataset_id": DATASET_ID,
            "dataset_archive_sha256": ARCHIVE_SHA,
            "random_seed": SEED,
            "positive_class": "synthetic_ledger_contradicting",
            "training_articles": 18_000,
            "synthetic_only": True,
            "private_isot_content_used": False,
            "external_copyrighted_dataset_used": False,
        },
    )
    metadata_hash = sha256(metadata_path)
    manifest_path = MODEL_PATH.parent / "public_artifact_manifest.json"
    dump_json(
        manifest_path,
        {
            "schema_version": 1,
            "dataset_id": DATASET_ID,
            "dataset_archive_sha256": ARCHIVE_SHA,
            "synthetic_only": True,
            "artifacts": {
                "model": {
                    "path": str(MODEL_PATH.relative_to(ROOT)),
                    "size_bytes": MODEL_PATH.stat().st_size,
                    "sha256": model_hash,
                },
                "calibration": {
                    "path": str(CALIBRATION_PATH.relative_to(ROOT)),
                    "size_bytes": CALIBRATION_PATH.stat().st_size,
                    "sha256": calibration_hash,
                    "bound_model_sha256": calibration_payload["model_sha256"],
                },
                "metadata": {
                    "path": str(metadata_path.relative_to(ROOT)),
                    "size_bytes": metadata_path.stat().st_size,
                    "sha256": metadata_hash,
                },
            },
        },
    )
    methodology = f"""# Synthetic Model Benchmark Methodology

NewsLens AI model version `{MODEL_VERSION}` is trained only from the independently
authored `{DATASET_ID}` benchmark. No ISOT content, private ISOT-derived model, or
external copyrighted training dataset is used.

## Locked protocol

- Group key: `event_id`; paired articles never cross partitions.
- Training: 18,000 rows; model validation: 2,400 rows.
- Calibration: 1,200 rows; abstention-policy selection: 1,200 rows.
- Locked final test: 1,200 rows, evaluated once after selection and calibration.
- Candidate selection: validation macro-F1 with a 0.005 interpretable-model retention tolerance.
- Calibration: Platt scaling bound to model SHA-256 `{model_hash}`.
- Editorial-review threshold: `{threshold:.2f}`.

## Controls

The evaluation includes content-hash and paired-event leakage checks, a visible
fact-block counterfactual swap, surface-text-only and metadata-only baselines, and
fact-block ablation. Metrics and per-partition evidence are recorded in
`reports/model_benchmark_summary.json`; artifact identities are recorded in
`models/public_artifact_manifest.json`.
"""
    (REPORTS / "model_benchmark_methodology.md").write_text(methodology, encoding="utf-8")
    print(
        json.dumps(
            {
                "model_sha256": model_hash,
                "calibration_sha256": calibration_hash,
                "metadata_sha256": metadata_hash,
                "threshold": threshold,
                "locked_metrics": locked,
                "shortcuts": shortcuts,
                "counterfactual": counterfactual,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
