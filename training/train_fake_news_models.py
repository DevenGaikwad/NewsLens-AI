"""Tune, compare, evaluate, and persist classical fake-news classifiers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from time import perf_counter

os.environ.setdefault("MPLCONFIGDIR", "/tmp/newslens-matplotlib")

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (  # noqa: E402
    FIGURES_DIR,
    MODEL_METADATA_PATH,
    MODEL_PATH,
    MODEL_VERSION,
    RANDOM_SEED,
    RAW_DATA_DIR,
    RESULTS_DIR,
)
from src.explainability import global_top_features  # noqa: E402
from src.utils import dump_json  # noqa: E402
from training.prepare_dataset import load_isot_dataset  # noqa: E402


COLORS = {0: "#496454", 1: "#813F39"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def base_pipeline(classifier) -> Pipeline:
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


def model_candidates() -> dict[str, tuple[Pipeline, dict[str, list[object]]]]:
    return {
        "Logistic Regression": (
            base_pipeline(
                LogisticRegression(
                    max_iter=1_200,
                    class_weight="balanced",
                    solver="liblinear",
                    random_state=RANDOM_SEED,
                )
            ),
            {"classifier__C": [0.5, 1.0, 2.0]},
        ),
        "Linear SVM": (
            base_pipeline(LinearSVC(class_weight="balanced", random_state=RANDOM_SEED)),
            {"classifier__C": [0.5, 1.0, 2.0]},
        ),
        "Multinomial Naive Bayes": (
            base_pipeline(MultinomialNB()),
            {"classifier__alpha": [0.1, 0.5, 1.0]},
        ),
    }


def scores_for(estimator: Pipeline, x_test: pd.Series) -> np.ndarray:
    if hasattr(estimator, "predict_proba"):
        classes = list(estimator.classes_)
        return estimator.predict_proba(x_test)[:, classes.index(1)]
    decision = np.asarray(estimator.decision_function(x_test), dtype=float)
    return 1.0 / (1.0 + np.exp(-np.clip(decision, -30, 30)))


def evaluate(estimator: Pipeline, x_test: pd.Series, y_test: pd.Series) -> dict[str, float]:
    started = perf_counter()
    predicted = estimator.predict(x_test)
    elapsed = perf_counter() - started
    score = scores_for(estimator, x_test)
    return {
        "accuracy": accuracy_score(y_test, predicted),
        "precision": precision_score(y_test, predicted, zero_division=0),
        "recall": recall_score(y_test, predicted, zero_division=0),
        "f1": f1_score(y_test, predicted, zero_division=0),
        "macro_f1": f1_score(y_test, predicted, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_test, predicted, average="weighted", zero_division=0),
        "roc_auc": roc_auc_score(y_test, score),
        "pr_auc": average_precision_score(y_test, score),
        "mean_inference_ms_per_article": elapsed / len(x_test) * 1000,
    }


def create_eda_figures(frame: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid", font_scale=1.0)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    counts = frame["label"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=180)
    bars = ax.bar(["Reliable", "Misleading"], counts.values, color=[COLORS[0], COLORS[1]])
    ax.set_title(f"ISOT class distribution after preprocessing (n={len(frame):,})", weight="bold")
    ax.set_ylabel("Article count")
    ax.bar_label(bars, labels=[f"{value:,}" for value in counts.values], padding=4)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "class_distribution.png", bbox_inches="tight")
    plt.close(fig)

    plot_frame = frame.sample(n=min(12_000, len(frame)), random_state=RANDOM_SEED).copy()
    plot_frame["Class"] = plot_frame["label"].map({0: "Reliable", 1: "Misleading"})
    fig, ax = plt.subplots(figsize=(9.2, 5.2), dpi=180)
    sns.histplot(
        data=plot_frame,
        x="word_count",
        hue="Class",
        bins=50,
        stat="density",
        common_norm=False,
        element="step",
        palette={"Reliable": COLORS[0], "Misleading": COLORS[1]},
        ax=ax,
    )
    ax.set_xlim(0, float(plot_frame["word_count"].quantile(0.98)))
    ax.set_title(f"Article-length distribution by class (sample n={len(plot_frame):,})", weight="bold")
    ax.set_xlabel("Word count (98th percentile view)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "word_count_distribution.png", bbox_inches="tight")
    plt.close(fig)

    top_rows = []
    for label, class_name in [(0, "Reliable"), (1, "Misleading")]:
        texts = frame.loc[frame["label"] == label, "combined"].sample(
            n=min(4_000, int((frame["label"] == label).sum())), random_state=RANDOM_SEED
        )
        vectorizer = CountVectorizer(stop_words="english", max_features=5_000)
        matrix = vectorizer.fit_transform(texts)
        totals = np.asarray(matrix.sum(axis=0)).ravel()
        names = np.asarray(vectorizer.get_feature_names_out())
        for index in np.argsort(totals)[-12:]:
            top_rows.append({"term": names[index], "count": totals[index], "Class": class_name})
    ngrams = pd.DataFrame(top_rows)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), dpi=180)
    for ax, class_name, color in zip(axes, ["Reliable", "Misleading"], [COLORS[0], COLORS[1]], strict=True):
        subset = ngrams[ngrams["Class"] == class_name].sort_values("count")
        ax.barh(subset["term"], subset["count"], color=color)
        ax.set_title(f"Frequent unigrams: {class_name}", weight="bold")
        ax.set_xlabel("Corpus frequency (4,000-article sample)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "top_ngrams.png", bbox_inches="tight")
    plt.close(fig)


def create_evaluation_figures(
    champion: Pipeline,
    x_test: pd.Series,
    y_test: pd.Series,
    comparison: pd.DataFrame,
) -> None:
    predicted = champion.predict(x_test)
    scores = scores_for(champion, x_test)
    matrix = confusion_matrix(y_test, predicted)

    fig, ax = plt.subplots(figsize=(6.3, 5.2), dpi=190)
    sns.heatmap(
        matrix,
        annot=True,
        fmt=",d",
        cmap=sns.light_palette("#6D5947", as_cmap=True),
        xticklabels=["Reliable", "Misleading"],
        yticklabels=["Reliable", "Misleading"],
        ax=ax,
    )
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(f"Held-out confusion matrix (n={len(y_test):,})", weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "confusion_matrix.png", bbox_inches="tight")
    plt.close(fig)

    fpr, tpr, _ = roc_curve(y_test, scores)
    precision, recall, _ = precision_recall_curve(y_test, scores)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=190)
    axes[0].plot(fpr, tpr, color="#496454", linewidth=2.5, label=f"AUC={roc_auc_score(y_test, scores):.4f}")
    axes[0].plot([0, 1], [0, 1], linestyle="--", color="#77736C")
    axes[0].set(title="ROC curve", xlabel="False-positive rate", ylabel="True-positive rate")
    axes[0].legend()
    axes[1].plot(recall, precision, color="#813F39", linewidth=2.5, label=f"AP={average_precision_score(y_test, scores):.4f}")
    axes[1].set(title="Precision-recall curve", xlabel="Recall", ylabel="Precision")
    axes[1].legend()
    fig.suptitle(f"Champion-model discrimination (held-out n={len(y_test):,})", weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "roc_pr_curves.png", bbox_inches="tight")
    plt.close(fig)

    metric_names = ["accuracy", "macro_f1", "roc_auc", "pr_auc"]
    x_positions = np.arange(len(comparison))
    width = 0.19
    fig, ax = plt.subplots(figsize=(10.5, 5.3), dpi=190)
    for offset, metric in enumerate(metric_names):
        ax.bar(
            x_positions + (offset - 1.5) * width,
            comparison[metric],
            width,
            label=metric.replace("_", " ").title(),
        )
    ax.set_xticks(x_positions, comparison["model"], rotation=10)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Held-out model comparison", weight="bold")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.16), frameon=False)
    fig.subplots_adjust(bottom=0.24)
    fig.savefig(FIGURES_DIR / "model_comparison.png", bbox_inches="tight")
    plt.close(fig)

    try:
        features = global_top_features(champion, top_n=14)
        feature_rows = []
        for label, values in features.items():
            for value in values:
                feature_rows.append(
                    {
                        "term": value["term"],
                        "coefficient": value["coefficient"],
                        "Class": label.title(),
                    }
                )
        feature_frame = pd.DataFrame(feature_rows)
        fig, axes = plt.subplots(1, 2, figsize=(12.2, 6.0), dpi=190)
        for ax, class_name, color in zip(
            axes, ["Reliable", "Misleading"], [COLORS[0], COLORS[1]], strict=True
        ):
            subset = feature_frame[feature_frame["Class"] == class_name].copy()
            subset["magnitude"] = subset["coefficient"].abs()
            subset = subset.sort_values("magnitude")
            ax.barh(subset["term"], subset["magnitude"], color=color)
            ax.set_title(f"Global terms toward {class_name.lower()}", weight="bold")
            ax.set_xlabel("Absolute logistic coefficient")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "feature_importance.png", bbox_inches="tight")
        plt.close(fig)
        dump_json(RESULTS_DIR / "global_top_features.json", features)
    except ValueError:
        pass


def train(max_rows: int = 24_000) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame, profile = load_isot_dataset(RAW_DATA_DIR, max_rows=max_rows)
    create_eda_figures(frame)
    x_train, x_test, y_train, y_test = train_test_split(
        frame["combined"],
        frame["label"],
        test_size=0.20,
        stratify=frame["label"],
        random_state=RANDOM_SEED,
    )

    tuned: dict[str, GridSearchCV] = {}
    comparison_rows: list[dict[str, object]] = []
    for name, (pipeline, grid) in model_candidates().items():
        print(f"Tuning {name}...")
        started = perf_counter()
        search = GridSearchCV(
            pipeline,
            param_grid=grid,
            scoring="f1_macro",
            cv=3,
            n_jobs=2,
            refit=True,
            return_train_score=False,
        )
        search.fit(x_train, y_train)
        training_seconds = perf_counter() - started
        tuned[name] = search
        values = evaluate(search.best_estimator_, x_test, y_test)
        best_index = search.best_index_
        comparison_rows.append(
            {
                "model": name,
                **{key: round(float(value), 6) for key, value in values.items()},
                "cv_macro_f1_mean": round(float(search.best_score_), 6),
                "cv_macro_f1_std": round(float(search.cv_results_["std_test_score"][best_index]), 6),
                "training_time_seconds": round(training_seconds, 4),
                "best_params": json.dumps(search.best_params_, sort_keys=True),
            }
        )
    comparison = pd.DataFrame(comparison_rows).sort_values("cv_macro_f1_mean", ascending=False)

    best_cv = float(comparison.iloc[0]["cv_macro_f1_mean"])
    logistic_cv = float(
        comparison.loc[comparison["model"] == "Logistic Regression", "cv_macro_f1_mean"].iloc[0]
    )
    champion_name = "Logistic Regression" if best_cv - logistic_cv <= 0.01 else str(comparison.iloc[0]["model"])
    champion = clone(tuned[champion_name].best_estimator_)
    champion_started = perf_counter()
    champion.fit(x_train, y_train)
    champion_training_seconds = perf_counter() - champion_started
    final_metrics = evaluate(champion, x_test, y_test)

    joblib.dump(champion, MODEL_PATH, compress=3)
    comparison.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)
    predictions = champion.predict(x_test)
    report_frame = pd.DataFrame(classification_report(y_test, predictions, output_dict=True)).T
    report_frame.to_csv(RESULTS_DIR / "classification_report.csv")

    scores = scores_for(champion, x_test)
    error_frame = pd.DataFrame(
        {
            "text_hash": x_test.map(lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()),
            "true_label": y_test.values,
            "predicted_label": predictions,
            "misleading_probability": scores,
            "word_count": x_test.str.split().str.len(),
        }
    )
    error_frame[error_frame["true_label"] != error_frame["predicted_label"]].to_csv(
        RESULTS_DIR / "error_analysis.csv", index=False
    )

    champion_row = comparison[comparison["model"] == champion_name].iloc[0]
    metrics_payload = {
        **{key: round(float(value), 6) for key, value in final_metrics.items()},
        "cv_macro_f1_mean": round(float(champion_row["cv_macro_f1_mean"]), 6),
        "cv_macro_f1_std": round(float(champion_row["cv_macro_f1_std"]), 6),
        "training_time_seconds": round(champion_training_seconds, 4),
        "test_samples": int(len(y_test)),
        "train_samples": int(len(y_train)),
        "random_seed": RANDOM_SEED,
        "positive_class": "misleading (1)",
    }
    dump_json(RESULTS_DIR / "model_metrics.json", metrics_payload)
    dump_json(RESULTS_DIR / "dataset_profile.json", profile)

    metadata = {
        "model_version": MODEL_VERSION,
        "champion_model": champion_name,
        "pipeline": "TF-IDF word 1-2 grams + linear classifier",
        "best_params": tuned[champion_name].best_params_,
        "selection_rule": (
            "Highest 3-fold CV Macro F1; prefer Logistic Regression when within 0.01 "
            "for calibrated probabilities and direct coefficient explanations."
        ),
        "dataset": "ISOT Fake News Dataset",
        "dataset_url": (
            "https://onlineacademiccommunity.uvic.ca/isot/2022/11/27/"
            "fake-news-detection-datasets/"
        ),
        "training_sample_rows": int(len(frame)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "class_mapping": {"0": "reliable", "1": "misleading"},
        "feature_leakage_controls": [
            "exact duplicate removal before splitting",
            "source/subject columns excluded",
            "Reuters/byline markers neutralised",
            "vectorizer fitted inside training-only Pipeline",
        ],
        "true_csv_sha256": file_sha256(RAW_DATA_DIR / "True.csv"),
        "fake_csv_sha256": file_sha256(RAW_DATA_DIR / "Fake.csv"),
        "random_seed": RANDOM_SEED,
        "limitations": (
            "ISOT outlet, topic, period, and writing-style artefacts remain. This is a "
            "credibility-risk classifier, not an evidence-retrieval fact-checker."
        ),
    }
    dump_json(MODEL_METADATA_PATH, metadata)
    create_evaluation_figures(champion, x_test, y_test, comparison)
    print(json.dumps({"champion": champion_name, **metrics_payload}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-rows",
        type=int,
        default=24_000,
        help="Balanced maximum rows used for tuning; 0 uses every clean row.",
    )
    args = parser.parse_args()
    train(max_rows=args.max_rows or None)


if __name__ == "__main__":
    main()
