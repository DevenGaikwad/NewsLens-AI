"""TXT and PDF ingestion with file-size and extraction checks."""

from __future__ import annotations

from io import BytesIO
from pathlib import PurePath, PurePosixPath

from .config import (
    MAX_EXTRACTED_TEXT_CHARS,
    MAX_PDF_PAGES,
    MAX_UPLOAD_BYTES,
)
from .text_preprocessor import clean_article_text
from .utils import word_count


class FileParseError(RuntimeError):
    """A file-upload issue that can be shown directly to the user."""


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise FileParseError("The text-file character encoding is unsupported.")


def safe_upload_filename(filename: str) -> str:
    """Return a display-safe basename or reject traversal/control characters."""

    value = str(filename or "").strip()
    if (
        not value
        or "\x00" in value
        or any(ord(char) < 32 for char in value)
        or "/" in value
        or "\\" in value
        or PurePosixPath(value).name != value
        or PurePath(value).name != value
        or value in {".", ".."}
    ):
        raise FileParseError("The uploaded filename is invalid.")
    return value


def parse_uploaded_file(filename: str, data: bytes) -> str:
    """Extract plain text from a supported in-memory upload."""

    if not data:
        raise FileParseError("The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise FileParseError("The file exceeds the 10 MB upload limit.")
    safe_name = safe_upload_filename(filename)
    suffix = PurePath(safe_name).suffix.lower()
    if suffix == ".txt":
        text = _decode_text(data)
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise FileParseError("PDF support needs the pypdf package.") from exc
        try:
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted:
                raise FileParseError("Password-protected PDFs are not supported.")
            if len(reader.pages) > MAX_PDF_PAGES:
                raise FileParseError(f"PDF files are limited to {MAX_PDF_PAGES} pages.")
            chunks: list[str] = []
            extracted_chars = 0
            for page in reader.pages:
                chunk = page.extract_text() or ""
                extracted_chars += len(chunk)
                if extracted_chars > MAX_EXTRACTED_TEXT_CHARS:
                    raise FileParseError("The PDF contains too much extracted text.")
                chunks.append(chunk)
            text = "\n".join(chunks)
        except FileParseError:
            raise
        except Exception as exc:
            raise FileParseError("Text could not be extracted from this PDF.") from exc
    else:
        raise FileParseError("Supported upload formats are .txt and text-based .pdf files.")
    text = clean_article_text(text, remove_source_markers=False)
    if word_count(text) < 40:
        raise FileParseError(
            "The file contains too little extractable text. Scanned PDFs need OCR before upload."
        )
    return text
