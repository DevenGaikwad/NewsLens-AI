"""Authoritative native router for the NewsLens AI Streamlit application."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent

PAGES = (
    st.Page(
        ROOT / "pages" / "00_News_Desk.py",
        title="News Desk",
        default=True,
    ),
    st.Page(
        ROOT / "pages" / "01_Analyse_Article.py",
        title="Analyse Article",
        url_path="analyse-article",
    ),
    st.Page(
        ROOT / "pages" / "02_Model_Performance.py",
        title="Model Accountability",
        url_path="model-accountability",
    ),
    st.Page(
        ROOT / "pages" / "03_Dataset_EDA.py",
        title="Dataset Analysis",
        url_path="dataset-analysis",
    ),
    st.Page(
        ROOT / "pages" / "04_Analysis_History.py",
        title="Editorial Archive",
        url_path="editorial-archive",
    ),
    st.Page(
        ROOT / "pages" / "05_Research_About.py",
        title="Research & About",
        url_path="research-about",
    ),
)


selected_page = st.navigation(PAGES, position="top")
selected_page.run()
