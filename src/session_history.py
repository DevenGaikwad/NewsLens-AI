"""Session-isolated SQLite paths for the public Streamlit interface.

The database CRUD layer remains path-parameterized and reusable. This adapter
chooses a private per-session file for UI requests so one public visitor cannot
open another visitor's archive. Trusted, single-user local installations may
explicitly opt into the durable project-local database.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import secrets
import tempfile

import streamlit as st

from .config import DATABASE_PATH


SESSION_KEY = "_newslens_private_history_id"
VALID_HISTORY_MODES = {"session", "persistent"}


def history_mode() -> str:
    """Return the configured history mode; fail closed to session isolation."""

    requested = os.getenv("NEWSLENS_HISTORY_MODE", "session").strip().lower()
    return requested if requested in VALID_HISTORY_MODES else "session"


def scoped_history_path(session_id: str, root: Path | None = None) -> Path:
    """Map an opaque session identifier to a non-guessable SQLite filename."""

    if not session_id:
        raise ValueError("A non-empty session identifier is required.")
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    session_root = root or Path(tempfile.gettempdir()) / "newslens-ai-sessions"
    session_root.mkdir(parents=True, exist_ok=True)
    return session_root / f"history-{digest}.db"


def session_history_path() -> Path:
    """Return the current visitor's database path.

    ``session`` is the safe default for public hosting. ``persistent`` is an
    explicit opt-in intended only for a trusted, single-user local runtime.
    """

    if history_mode() == "persistent":
        return DATABASE_PATH
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = secrets.token_urlsafe(32)
    return scoped_history_path(str(st.session_state[SESSION_KEY]))
