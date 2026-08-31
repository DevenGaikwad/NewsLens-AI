"""Load, clean, de-duplicate, and optionally sample the ISOT dataset."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RANDOM_SEED  # noqa: E402
from src.text_preprocessor import text_for_model  # noqa: E402
from src.utils import word_count  # noqa: E402


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_isot_dataset(raw_dir: Path, max_rows: int | None = None) -> tuple[pd.DataFrame, dict[str, int]]:
    true_path = raw_dir / "True.csv"
    fake_path = raw_dir / "Fake.csv"
    if not true_path.exists() or not fake_path.exists():
        raise FileNotFoundError(
            "ISOT CSV files are missing. Run: python training/download_data.py --dataset isot"
        )
    true_frame = pd.read_csv(true_path)
    fake_frame = pd.read_csv(fake_path)
    true_frame["label"] = 0
    fake_frame["label"] = 1
    raw_rows = len(true_frame) + len(fake_frame)
    frame = pd.concat([true_frame, fake_frame], ignore_index=True)
    frame["title"] = frame["title"].fillna("").astype(str).str.strip()
    frame["text"] = frame["text"].fillna("").astype(str)
    frame["combined"] = (frame["title"] + ". " + frame["text"]).map(text_for_model)
    frame["word_count"] = frame["combined"].map(word_count)
    frame = frame[frame["word_count"] >= 40].copy()
    frame["text_hash"] = frame["combined"].map(_hash_text)

    label_counts = frame.groupby("text_hash")["label"].nunique()
    conflicting = set(label_counts[label_counts > 1].index)
    conflicting_removed = int(frame["text_hash"].isin(conflicting).sum())
    if conflicting:
        frame = frame[~frame["text_hash"].isin(conflicting)].copy()
    before_duplicates = len(frame)
    frame = frame.drop_duplicates(subset=["text_hash"], keep="first").copy()
    duplicates_removed = before_duplicates - len(frame)
    clean_rows_before_sampling = len(frame)

    if max_rows and len(frame) > max_rows:
        per_class = max_rows // 2
        sampled = []
        for label in (0, 1):
            group = frame[frame["label"] == label]
            sampled.append(group.sample(n=min(per_class, len(group)), random_state=RANDOM_SEED))
        frame = pd.concat(sampled, ignore_index=True).sample(frac=1, random_state=RANDOM_SEED)

    profile = {
        "raw_rows": int(raw_rows),
        "clean_rows": int(clean_rows_before_sampling),
        "training_sample_rows": int(len(frame)),
        "duplicates_removed": int(duplicates_removed),
        "conflicting_label_rows_removed": conflicting_removed,
        "short_or_empty_rows_removed": int(raw_rows - clean_rows_before_sampling - duplicates_removed - conflicting_removed),
        "reliable_rows": int((frame["label"] == 0).sum()),
        "misleading_rows": int((frame["label"] == 1).sum()),
    }
    return frame.reset_index(drop=True), profile


if __name__ == "__main__":
    data, summary = load_isot_dataset(PROJECT_ROOT / "data" / "raw")
    print(summary)
    print(data[["label", "word_count", "subject"]].head())
