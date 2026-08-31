"""Shared NewsLens AI masthead used beneath Streamlit's native top router."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = ROOT / "assets" / "logo.svg"

def _logo_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def render_navigation(active: str = "") -> None:
    """Render branding only; ``st.navigation`` owns every internal route.

    ``active`` is retained for compatibility with the established page calls.
    The native navigation widget supplies the active-page state accessibly.
    """

    del active
    logo = _logo_uri()
    logo_html = f'<img src="{logo}" alt="" aria-hidden="true">' if logo else ""
    st.markdown(
        (
            '<header class="nl-masthead" role="banner">'
            f'<div class="nl-brand">{logo_html}<span>NewsLens AI</span></div>'
            '<div class="nl-descriptor">Editorial Credibility-Risk System</div>'
            "</header>"
        ),
        unsafe_allow_html=True,
    )
