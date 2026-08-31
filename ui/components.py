"""Reusable editorial components shared across every Streamlit page."""

from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Iterable, Sequence

import streamlit as st

from src.config import COPYRIGHT_NOTICE, PROJECT_AUTHOR

from .navigation import render_navigation
from .theme import apply_theme


ROOT = Path(__file__).resolve().parents[1]
HERO_ART_PATH = ROOT / "assets" / "editorial_masthead.svg"


def _escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def _image_uri(path: Path) -> str:
    if not path.exists():
        return ""
    suffix = path.suffix.lower().lstrip(".")
    mime = "svg+xml" if suffix == "svg" else suffix
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def configure_page(title: str, icon: str = "📰", *, active: str = "home") -> None:
    """Set page metadata, apply the theme, and render shared navigation."""

    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_theme()
    render_navigation(active)


def hero(
    eyebrow: str,
    title: str,
    description: str,
    *,
    primary_label: str = "Analyse an Article",
    primary_href: str = "pages/01_Analyse_Article.py",
    secondary_label: str = "Open Archive",
    secondary_href: str = "pages/04_Analysis_History.py",
    technical_tags: Sequence[str] = (),
) -> None:
    """Render the newsroom hero with native, same-tab Streamlit page links."""

    art_uri = _image_uri(HERO_ART_PATH)
    title_html = "<br>".join(_escape(title).splitlines())
    tags = " · ".join(_escape(tag) for tag in technical_tags)
    art = (
        f'<img src="{art_uri}" alt="Original abstract editorial illustration of layered news pages">'
        if art_uri
        else ""
    )
    with st.container(key="nl_hero"):
        copy, visual = st.columns([1.18, 0.82], gap=None, vertical_alignment="center")
        with copy:
            st.markdown(
                f"""
<div class="editorial-hero-copy">
  <div class="eyebrow">{_escape(eyebrow)}</div>
  <h1>{title_html}</h1>
  <p>{_escape(description)}</p>
</div>
""",
                unsafe_allow_html=True,
            )
            with st.container(
                key="nl_hero_actions",
                horizontal=True,
                horizontal_alignment="left",
                gap="small",
            ):
                st.page_link(
                    primary_href,
                    label=primary_label,
                    use_container_width=True,
                )
                st.page_link(
                    secondary_href,
                    label=secondary_label,
                    use_container_width=True,
                )
            st.markdown(
                f'<div class="technical-tags">{tags}</div>',
                unsafe_allow_html=True,
            )
        with visual:
            st.markdown(
                f'<div class="editorial-hero-art">{art}</div>',
                unsafe_allow_html=True,
            )


def page_header(eyebrow: str, title: str, description: str) -> None:
    title_html = "<br>".join(_escape(title).splitlines())
    st.markdown(
        f"""
<header class="page-hero">
  <div><div class="eyebrow">{_escape(eyebrow)}</div><h1>{title_html}</h1></div>
  <p>{_escape(description)}</p>
</header>
""",
        unsafe_allow_html=True,
    )


def editorial_strip(items: Sequence[str]) -> None:
    content = " ◆ ".join(_escape(item) for item in items)
    st.markdown(f'<div class="editorial-strip">{content}</div>', unsafe_allow_html=True)


def section_heading(kicker: str, title: str, body: str = "") -> None:
    st.markdown(
        f"""
<section class="section-heading">
  <div><div class="section-kicker">{_escape(kicker)}</div><h2>{_escape(title)}</h2></div>
  <p>{_escape(body)}</p>
</section>
""",
        unsafe_allow_html=True,
    )


def section_card(title: str, body: str, *, label: str = "") -> None:
    label_html = f'<div class="technical-label">{_escape(label)}</div>' if label else ""
    st.markdown(
        f'<article class="editorial-card">{label_html}<h3>{_escape(title)}</h3>'
        f"<p>{_escape(body)}</p></article>",
        unsafe_allow_html=True,
    )


def workflow_steps(items: Sequence[tuple[str, str]]) -> None:
    rows = "".join(
        f'<div class="workflow-item"><div><strong>{_escape(title)}</strong>'
        f"<span>{_escape(body)}</span></div></div>"
        for title, body in items
    )
    st.markdown(f'<div class="workflow-list">{rows}</div>', unsafe_allow_html=True)


def metric_strip(items: Sequence[tuple[str, object, str]]) -> None:
    rows = "".join(
        (
            '<div class="metric-item">'
            f'<div class="metric-label">{_escape(label)}</div>'
            f'<div class="metric-value">{_escape(value)}</div>'
            f'<div class="metric-note">{_escape(note)}</div>'
            "</div>"
        )
        for label, value, note in items
    )
    st.markdown(f'<div class="metric-strip">{rows}</div>', unsafe_allow_html=True)


def _verdict_style(label: str) -> tuple[str, str]:
    if label == "Lower misleading-content risk indicated":
        return "reliable", "Lower linguistic risk signal"
    if label == "Higher misleading-content risk indicated":
        return "misleading", "Higher linguistic risk signal"
    return "uncertain", "Human editorial review required"


def result_status(
    label: str,
    *,
    confidence: float | None = None,
    interpretation: str = "",
) -> None:
    css_class, risk_label = _verdict_style(label)
    probability = ""
    if confidence is not None:
        probability = (
            '<div class="verdict-probability">'
            f"<strong>{confidence:.1%}</strong><span>calibrated confidence</span></div>"
        )
    st.markdown(
        f"""
<section class="verdict-panel {css_class}">
  <div class="verdict-label">Editorial risk signal · {risk_label}</div>
  <div class="verdict-title">{_escape(label)}</div>
  <p>{_escape(interpretation)}</p>
  {probability}
</section>
""",
        unsafe_allow_html=True,
    )


def reading_panel(title: str, text: str, *, meta: str = "") -> None:
    st.markdown(
        f"""
<section class="reading-panel">
  <div class="technical-label">Executive Summary</div>
  <h3>{_escape(title)}</h3>
  <p>{_escape(text)}</p>
  <div class="reading-meta">{_escape(meta)}</div>
</section>
""",
        unsafe_allow_html=True,
    )


def metadata_grid(items: Sequence[tuple[str, object]]) -> None:
    rows = "".join(
        (
            '<div class="metadata-item">'
            f'<span class="label">{_escape(label)}</span>'
            f'<span class="value">{_escape(value or "Not available")}</span>'
            "</div>"
        )
        for label, value in items
    )
    st.markdown(f'<div class="metadata-panel metadata-grid">{rows}</div>', unsafe_allow_html=True)


def evidence_terms(
    label: str,
    values: Iterable[dict[str, object]],
    *,
    direction: str,
) -> None:
    css_class = "misleading" if direction == "misleading" else "reliable"
    chips = []
    for value in values:
        term = _escape(value.get("term", ""))
        contribution = float(value.get("contribution", 0))
        chips.append(
            f'<span class="evidence-chip {css_class}">{term} · {contribution:+.4f}</span>'
        )
    chip_html = "".join(chips) or '<span class="metric-note">No observed terms available.</span>'
    st.markdown(
        f'<div class="evidence-group"><div class="technical-label">{_escape(label)}</div>'
        f"<div>{chip_html}</div></div>",
        unsafe_allow_html=True,
    )


def callout(label: str, body: str, *, kind: str = "neutral") -> None:
    css_class = kind if kind in {"warning", "danger", "success"} else ""
    st.markdown(
        f'<div class="callout {css_class}"><strong>{_escape(label)}:</strong> '
        f"{_escape(body)}</div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str) -> None:
    st.markdown(
        f'<section class="empty-state"><h3>{_escape(title)}</h3><p>{_escape(body)}</p></section>',
        unsafe_allow_html=True,
    )


def footer(
    left: str = "NewsLens AI · Local-first analysis",
    right: str = "Responsible academic AI",
) -> None:
    st.markdown(
        (
            '<footer class="nl-footer">'
            f'<div class="nl-footer-context"><span>{_escape(left)}</span><span>{_escape(right)}</span></div>'
            '<div class="nl-footer-owner">'
            f'<span>NewsLens AI · Designed and developed by {_escape(PROJECT_AUTHOR)}</span>'
            f'<span>{_escape(COPYRIGHT_NOTICE)}</span>'
            "</div></footer>"
        ),
        unsafe_allow_html=True,
    )
