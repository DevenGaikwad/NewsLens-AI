"""Streamlit script smoke tests with no browser or network dependency."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "app.py",
    ROOT / "pages/01_Analyse_Article.py",
    ROOT / "pages/02_Model_Performance.py",
    ROOT / "pages/03_Dataset_EDA.py",
    ROOT / "pages/04_Analysis_History.py",
    ROOT / "pages/05_Research_About.py",
]


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda path: path.stem)
def test_streamlit_page_starts_without_exception(script: Path) -> None:
    app = AppTest.from_file(str(script), default_timeout=20).run()
    assert not app.exception
