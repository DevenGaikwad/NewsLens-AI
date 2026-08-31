"""Local linear TF-IDF feature-contribution explanations."""

from __future__ import annotations

from typing import Any

import numpy as np


def _linear_coefficients(classifier: Any) -> np.ndarray:
    if hasattr(classifier, "coef_"):
        values = np.asarray(classifier.coef_)
        return values[0] if values.ndim == 2 else values
    calibrated = getattr(classifier, "calibrated_classifiers_", None)
    if calibrated:
        coefs = []
        for item in calibrated:
            estimator = getattr(item, "estimator", None)
            if estimator is not None and hasattr(estimator, "coef_"):
                coefs.append(np.asarray(estimator.coef_)[0])
        if coefs:
            return np.mean(coefs, axis=0)
    raise ValueError("The saved classifier does not expose linear coefficients.")


def explain_linear_prediction(
    pipeline: Any,
    model_text: str,
    top_n: int = 8,
) -> dict[str, list[dict[str, float | str]]]:
    """Return observed terms pushing toward misleading or reliable classes."""

    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["classifier"]
    vector = vectorizer.transform([model_text])
    coefficients = _linear_coefficients(classifier)
    contributions = vector.multiply(coefficients).toarray()[0]
    names = np.asarray(vectorizer.get_feature_names_out())
    observed = vector.toarray()[0] > 0
    indices = np.flatnonzero(observed)
    positive = sorted(indices, key=lambda index: contributions[index], reverse=True)[:top_n]
    negative = sorted(indices, key=lambda index: contributions[index])[:top_n]

    def pack(items: list[int]) -> list[dict[str, float | str]]:
        return [
            {"term": str(names[index]), "contribution": round(float(contributions[index]), 5)}
            for index in items
            if abs(contributions[index]) > 0
        ]

    return {"supports_misleading": pack(positive), "supports_reliable": pack(negative)}


def global_top_features(pipeline: Any, top_n: int = 20) -> dict[str, list[dict[str, float | str]]]:
    """Return coefficient-ranked vocabulary terms for model inspection."""

    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["classifier"]
    names = np.asarray(vectorizer.get_feature_names_out())
    coefficients = _linear_coefficients(classifier)
    pos = np.argsort(coefficients)[-top_n:][::-1]
    neg = np.argsort(coefficients)[:top_n]
    return {
        "misleading": [
            {"term": str(names[index]), "coefficient": round(float(coefficients[index]), 5)}
            for index in pos
        ],
        "reliable": [
            {"term": str(names[index]), "coefficient": round(float(coefficients[index]), 5)}
            for index in neg
        ],
    }
