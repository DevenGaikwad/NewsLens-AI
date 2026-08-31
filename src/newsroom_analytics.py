"""Privacy-safe aggregate newsroom metrics for one visitor's session archive."""

from __future__ import annotations

from typing import Any

import pandas as pd


CONFIDENCE_ORDER = ["Review", "Moderate", "High"]


def newsroom_summary(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {
            "analysed_articles": 0,
            "editorial_review_rate": 0.0,
            "inconclusive_rate": 0.0,
            "average_inference_latency_seconds": 0.0,
        }
    review_required = pd.to_numeric(frame["review_required"], errors="coerce").fillna(0).astype(bool)
    return {
        "analysed_articles": int(len(frame)),
        "editorial_review_rate": float(review_required.mean()),
        "inconclusive_rate": float((frame["review_status"] == "Inconclusive").mean()),
        "average_inference_latency_seconds": float(
            pd.to_numeric(frame["processing_time"], errors="coerce").fillna(0).mean()
        ),
        "pending_reviews": int((frame["review_status"] == "Pending review").sum()),
    }


def risk_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["Outcome", "Count"])
    return (
        frame["prediction_label"]
        .fillna("Editorial review required")
        .value_counts()
        .rename_axis("Outcome")
        .reset_index(name="Count")
    )


def confidence_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["Confidence band", "Count"])
    values = frame["confidence_band"].fillna("Review")
    counts = values.value_counts().reindex(CONFIDENCE_ORDER, fill_value=0)
    return counts.rename_axis("Confidence band").reset_index(name="Count")


def review_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["Review status", "Count"])
    return (
        frame["review_status"]
        .fillna("Pending review")
        .value_counts()
        .rename_axis("Review status")
        .reset_index(name="Count")
    )


def activity_over_time(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["Date", "Analyses"])
    timestamps = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce").dropna()
    if timestamps.empty:
        return pd.DataFrame(columns=["Date", "Analyses"])
    return (
        timestamps.dt.date.value_counts().sort_index().rename_axis("Date").reset_index(name="Analyses")
    )


def privacy_safe_analytics_export(frame: pd.DataFrame) -> pd.DataFrame:
    """Return only aggregates; never include article text, titles, notes, or URLs."""

    summary = newsroom_summary(frame)
    return pd.DataFrame(
        [
            {"metric": "Analysed articles", "value": summary["analysed_articles"]},
            {"metric": "Editorial-review rate", "value": summary["editorial_review_rate"]},
            {"metric": "Inconclusive rate", "value": summary["inconclusive_rate"]},
            {
                "metric": "Average end-to-end latency seconds",
                "value": summary["average_inference_latency_seconds"],
            },
            {"metric": "Pending reviews", "value": summary.get("pending_reviews", 0)},
        ]
    )
