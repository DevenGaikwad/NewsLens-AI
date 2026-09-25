"""Deterministic NewsLens synthetic benchmark generation and audit utilities."""

from .generator import (
    DATASET_ID,
    GENERATOR_VERSION,
    RANDOM_SEED,
    build_dataset,
    write_dataset_archive,
)

__all__ = [
    "DATASET_ID",
    "GENERATOR_VERSION",
    "RANDOM_SEED",
    "build_dataset",
    "write_dataset_archive",
]
