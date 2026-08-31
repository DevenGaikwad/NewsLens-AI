"""Evaluate the extractive summarizer on a fixed XSum test sample."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RANDOM_SEED, RAW_DATA_DIR, RESULTS_DIR  # noqa: E402
from src.extractive_summarizer import summarize_extractive  # noqa: E402
from src.utils import dump_json, word_count  # noqa: E402


TOKEN = re.compile(r"\b[a-z0-9]+\b")


def tokens(text: str) -> list[str]:
    return TOKEN.findall((text or "").lower())


def ngrams(items: list[str], size: int) -> Counter[tuple[str, ...]]:
    return Counter(tuple(items[index : index + size]) for index in range(len(items) - size + 1))


def overlap_scores(candidate: str, reference: str, size: int) -> tuple[float, float, float]:
    candidate_counts = ngrams(tokens(candidate), size)
    reference_counts = ngrams(tokens(reference), size)
    overlap = sum((candidate_counts & reference_counts).values())
    candidate_total = sum(candidate_counts.values())
    reference_total = sum(reference_counts.values())
    precision = overlap / candidate_total if candidate_total else 0.0
    recall = overlap / reference_total if reference_total else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def lcs_length(left: list[str], right: list[str]) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = [0] * (len(right) + 1)
    for item in left:
        current = [0]
        for index, other in enumerate(right, start=1):
            current.append(previous[index - 1] + 1 if item == other else max(previous[index], current[-1]))
        previous = current
    return previous[-1]


def rouge_l(candidate: str, reference: str) -> tuple[float, float, float]:
    candidate_tokens = tokens(candidate)
    reference_tokens = tokens(reference)
    length = lcs_length(candidate_tokens, reference_tokens)
    precision = length / len(candidate_tokens) if candidate_tokens else 0.0
    recall = length / len(reference_tokens) if reference_tokens else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluate(parquet_path: Path, sample_size: int = 150) -> None:
    if not parquet_path.exists():
        raise FileNotFoundError(
            "XSum parquet is missing. Run: python training/download_data.py --dataset xsum"
        )
    frame = pd.read_parquet(parquet_path, columns=["document", "summary", "id"])
    frame = frame[
        (frame["document"].map(word_count) >= 100)
        & (frame["summary"].map(word_count) >= 8)
    ]
    sample = frame.sample(n=min(sample_size, len(frame)), random_state=RANDOM_SEED)
    rows: list[dict[str, object]] = []
    for item in sample.itertuples(index=False):
        result = summarize_extractive(item.document, length="Medium")
        r1 = overlap_scores(result.summary, item.summary, 1)
        r2 = overlap_scores(result.summary, item.summary, 2)
        rl = rouge_l(result.summary, item.summary)
        rows.append(
            {
                "id": str(item.id),
                "rouge1_precision": r1[0],
                "rouge1_recall": r1[1],
                "rouge1_f1": r1[2],
                "rouge2_precision": r2[0],
                "rouge2_recall": r2[1],
                "rouge2_f1": r2[2],
                "rougeL_precision": rl[0],
                "rougeL_recall": rl[1],
                "rougeL_f1": rl[2],
                "compression_ratio_pct": result.compression_ratio_pct,
                "latency_ms": result.processing_time_seconds * 1000,
                "original_words": result.original_word_count,
                "summary_words": result.summary_word_count,
            }
        )
    results = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_DIR / "summarization_per_sample_metrics.csv", index=False)
    payload = {
        "dataset": "XSum test split",
        "dataset_url": "https://huggingface.co/datasets/EdinburghNLP/xsum",
        "sample_size": len(results),
        "random_seed": RANDOM_SEED,
        "method": "TF-IDF centroid extractive - Medium",
        "rouge1_precision": mean(results["rouge1_precision"]),
        "rouge1_recall": mean(results["rouge1_recall"]),
        "rouge1_f1": mean(results["rouge1_f1"]),
        "rouge2_precision": mean(results["rouge2_precision"]),
        "rouge2_recall": mean(results["rouge2_recall"]),
        "rouge2_f1": mean(results["rouge2_f1"]),
        "rougeL_precision": mean(results["rougeL_precision"]),
        "rougeL_recall": mean(results["rougeL_recall"]),
        "rougeL_f1": mean(results["rougeL_f1"]),
        "mean_compression_ratio_pct": mean(results["compression_ratio_pct"]),
        "mean_latency_ms": mean(results["latency_ms"]),
        "qualitative_note": (
            "XSum references are highly abstractive one-sentence summaries. Extractive overlap is "
            "therefore conservative; ROUGE does not by itself measure factual consistency or readability."
        ),
    }
    payload = {
        key: round(float(value), 6) if isinstance(value, (float, int)) and key not in {"sample_size", "random_seed"} else value
        for key, value in payload.items()
    }
    dump_json(RESULTS_DIR / "summarization_metrics.json", payload)
    print(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, default=RAW_DATA_DIR / "xsum-test.parquet")
    parser.add_argument("--sample-size", type=int, default=150)
    args = parser.parse_args()
    evaluate(args.parquet, args.sample_size)


if __name__ == "__main__":
    main()
