"""Shared deterministic fixtures for unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_article() -> str:
    return (PROJECT_ROOT / "data/sample/reliable_style_article.txt").read_text(encoding="utf-8")
