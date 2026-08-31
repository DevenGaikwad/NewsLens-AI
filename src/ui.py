"""Compatibility re-export for the componentized editorial UI package.

New application code may import from :mod:`ui` directly. This module remains so
older notebooks, tests, and documentation examples continue to resolve.
"""

from ui import (  # noqa: F401
    callout,
    configure_page,
    editorial_strip,
    empty_state,
    evidence_terms,
    footer,
    hero,
    metadata_grid,
    metric_strip,
    page_header,
    reading_panel,
    result_status,
    section_card,
    section_heading,
    workflow_steps,
)

__all__ = [
    "callout",
    "configure_page",
    "editorial_strip",
    "empty_state",
    "evidence_terms",
    "footer",
    "hero",
    "metadata_grid",
    "metric_strip",
    "page_header",
    "reading_panel",
    "result_status",
    "section_card",
    "section_heading",
    "workflow_steps",
]
