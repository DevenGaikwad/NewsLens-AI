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


def test_analysis_replaces_prior_input_and_fresh_session_is_deterministic() -> None:
    script = ROOT / "pages/01_Analyse_Article.py"
    realistic = (
        "A municipal transport committee reviewed bus timetables, accessibility requests, "
        "maintenance schedules, and public comments. Officials said no route changes would "
        "occur before consultation, while residents asked about school services, evening "
        "connections, and supporting cost estimates. Additional minutes described the meeting "
        "procedure and public feedback period."
    )
    fabricated = (
        "A purple glass moon landed beside a village library and began broadcasting tomorrow's "
        "weather. The invented story names no observatory, supplies no measurements, cites no "
        "evidence, and describes an impossible classroom event without structured comparison "
        "fields. Additional witnesses were fictional and no external claim is intended."
    )

    app = AppTest.from_file(str(script), default_timeout=30).run()
    app.text_area[0].set_value(realistic).run()
    app.button[2].click().run()
    first = dict(app.session_state["last_analysis"])

    app.text_area[0].set_value(fabricated).run()
    app.button[2].click().run()
    second = dict(app.session_state["last_analysis"])

    fresh = AppTest.from_file(str(script), default_timeout=30).run()
    fresh.text_area[0].set_value(realistic).run()
    fresh.button[2].click().run()
    repeated = dict(fresh.session_state["last_analysis"])

    assert first["article_hash"] != second["article_hash"]
    assert first["misleading_probability"] != second["misleading_probability"]
    assert first["supported_scope"] is second["supported_scope"] is False
    assert first["review_status"] == second["review_status"] == "Pending review"
    assert repeated["article_hash"] == first["article_hash"]
    assert repeated["misleading_probability"] == first["misleading_probability"]
    assert any(
        "Outside supported comparison scope" in str(block.value)
        for block in fresh.markdown
    )
