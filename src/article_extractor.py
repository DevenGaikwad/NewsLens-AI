"""Safe URL validation and layered news-article extraction."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

from .config import (
    MAX_ARTICLE_RESPONSE_BYTES,
    MAX_REDIRECTS,
    MAX_URL_LENGTH,
    REQUEST_TIMEOUT_SECONDS,
)
from .text_preprocessor import clean_article_text
from .utils import domain_from_url, reading_time_minutes, word_count


class ArticleExtractionError(RuntimeError):
    """A user-correctable extraction failure."""


@dataclass(frozen=True)
class ArticleData:
    text: str
    title: str = "Untitled article"
    author: str = "Not available"
    publication_date: str = "Not available"
    source_url: str = ""
    source_domain: str = ""
    extractor: str = ""
    word_count: int = 0
    reading_time_minutes: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REDIRECT_STATUSES = {301, 302, 303, 307, 308}


def _resolved_public_addresses(hostname: str, port: int) -> set[str]:
    """Resolve a host and fail closed unless every answer is globally routable."""

    try:
        records = socket.getaddrinfo(hostname, port, 0, socket.SOCK_STREAM)
    except (socket.gaierror, OSError) as exc:
        raise ArticleExtractionError("The website hostname could not be resolved.") from exc
    addresses = {item[4][0].split("%", 1)[0] for item in records if item[4]}
    if not addresses:
        raise ArticleExtractionError("The website hostname could not be resolved.")
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise ArticleExtractionError("The website resolved to an invalid network address.") from exc
        if not ip.is_global:
            raise ArticleExtractionError("Local or private network URLs are blocked.")
    return addresses


def _validate_public_target(url: str) -> tuple[str, set[str]]:
    """Validate one request/redirect target and return its public DNS answers."""

    value = (url or "").strip()
    if not value or len(value) > MAX_URL_LENGTH or any(ord(char) < 32 for char in value):
        raise ArticleExtractionError("Enter a valid public article URL.")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ArticleExtractionError("Enter a complete public http:// or https:// URL.")
    if parsed.username or parsed.password:
        raise ArticleExtractionError("URLs containing credentials are not supported.")
    if "%" in parsed.netloc or "\\" in parsed.netloc:
        raise ArticleExtractionError("Encoded or malformed hostnames are not supported.")
    try:
        hostname = parsed.hostname.rstrip(".").encode("idna").decode("ascii").lower()
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except (UnicodeError, ValueError) as exc:
        raise ArticleExtractionError("The article URL contains an invalid hostname or port.") from exc
    if (
        hostname in {"localhost", "0.0.0.0"}
        or hostname.endswith((".localhost", ".local"))
        or re.fullmatch(r"(?:0x[0-9a-f]+|\d+)", hostname, flags=re.IGNORECASE)
    ):
        raise ArticleExtractionError("Local or private network URLs are blocked.")
    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None
    if literal is not None:
        if not literal.is_global:
            raise ArticleExtractionError("Local or private network URLs are blocked.")
        addresses = {str(literal)}
    else:
        numeric_parts = hostname.split(".")
        if len(numeric_parts) == 4 and all(
            re.fullmatch(r"(?:0x[0-9a-f]+|0[0-7]+|\d+)", part, flags=re.IGNORECASE)
            for part in numeric_parts
        ):
            raise ArticleExtractionError("Obfuscated numeric hostnames are not supported.")
        addresses = _resolved_public_addresses(hostname, port)
    return value, addresses


def _validate_public_url(url: str) -> str:
    """Compatibility wrapper used by tests and callers needing validation only."""

    return _validate_public_target(url)[0]


def _peer_address(response: Any) -> str | None:
    """Best-effort peer-IP check against DNS rebinding when urllib3 exposes it."""

    raw = getattr(response, "raw", None)
    connection = getattr(raw, "_connection", None) or getattr(raw, "connection", None)
    sock = getattr(connection, "sock", None)
    if sock is None:
        return None
    try:
        return str(sock.getpeername()[0]).split("%", 1)[0]
    except (AttributeError, OSError, TypeError):
        return None


def _limited_response_text(response: Any) -> str:
    """Read a streamed response with a decoded-size ceiling."""

    length = response.headers.get("content-length")
    if length:
        try:
            if int(length) > MAX_ARTICLE_RESPONSE_BYTES:
                raise ArticleExtractionError("The article response exceeds the 5 MB download limit.")
        except ValueError:
            pass
    if hasattr(response, "iter_content"):
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_ARTICLE_RESPONSE_BYTES:
                raise ArticleExtractionError("The article response exceeds the 5 MB download limit.")
            chunks.append(bytes(chunk))
        data = b"".join(chunks)
        encoding = getattr(response, "encoding", None) or "utf-8"
        try:
            return data.decode(encoding, errors="replace")
        except LookupError:
            return data.decode("utf-8", errors="replace")
    text = str(getattr(response, "text", ""))
    if len(text.encode("utf-8")) > MAX_ARTICLE_RESPONSE_BYTES:
        raise ArticleExtractionError("The article response exceeds the 5 MB download limit.")
    return text


def _download_public_html(url: str) -> tuple[str, str, dict[str, str]]:
    """Download HTML while independently validating every redirect destination."""

    try:
        import requests
    except ImportError as exc:
        raise ArticleExtractionError("The requests package is not installed.") from exc

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/124 Safari/537.36 NewsLensAI/1.0"
        )
    }
    session = requests.Session()
    session.trust_env = False
    current = url
    visited: set[str] = set()
    try:
        for redirect_number in range(MAX_REDIRECTS + 1):
            safe_url, resolved = _validate_public_target(current)
            if safe_url in visited:
                raise ArticleExtractionError("The article URL contains a redirect loop.")
            visited.add(safe_url)
            try:
                response = session.get(
                    safe_url,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    allow_redirects=False,
                    stream=True,
                )
            except requests.RequestException as exc:
                raise ArticleExtractionError(
                    "The article could not be downloaded. The site may be unavailable, "
                    "paywalled, or blocking automated extraction."
                ) from exc

            peer = _peer_address(response)
            if peer is not None:
                try:
                    peer_ip = ipaddress.ip_address(peer)
                except ValueError as exc:
                    raise ArticleExtractionError("The remote server address could not be verified.") from exc
                if not peer_ip.is_global or str(peer_ip) not in resolved:
                    raise ArticleExtractionError("The remote server address changed during validation.")

            if response.status_code in REDIRECT_STATUSES:
                location = response.headers.get("location")
                if not location:
                    raise ArticleExtractionError("The website returned an invalid redirect.")
                if redirect_number >= MAX_REDIRECTS:
                    raise ArticleExtractionError("The article URL exceeded the redirect limit.")
                current = urljoin(safe_url, location)
                close = getattr(response, "close", None)
                if callable(close):
                    close()
                continue

            try:
                response.raise_for_status()
            except requests.RequestException as exc:
                raise ArticleExtractionError(
                    "The article could not be downloaded. The site may be unavailable, "
                    "paywalled, or blocking automated extraction."
                ) from exc
            text = _limited_response_text(response)
            response_headers = {str(key).lower(): str(value) for key, value in response.headers.items()}
            return text, safe_url, response_headers
    finally:
        session.close()
    raise ArticleExtractionError("The article URL could not be resolved safely.")


def _metadata_value(metadata: Any, *names: str, default: str = "Not available") -> str:
    for name in names:
        value = getattr(metadata, name, None) if metadata is not None else None
        if value:
            if isinstance(value, (list, tuple)):
                return ", ".join(str(item) for item in value)
            return str(value)
    return default


def extract_article(url: str) -> ArticleData:
    """Extract the article through Trafilatura, then a BeautifulSoup fallback."""

    response_text, final_url, response_headers = _download_public_html(url)
    content_type = response_headers.get("content-type", "").lower()
    if "html" not in content_type and not response_text.lstrip().startswith("<"):
        raise ArticleExtractionError("The URL did not return an HTML article page.")

    title = "Untitled article"
    author = "Not available"
    publication_date = "Not available"
    extracted = ""
    extractor = ""
    try:
        import trafilatura

        document = trafilatura.bare_extraction(
            response_text,
            url=final_url,
            include_comments=False,
            include_tables=False,
            with_metadata=True,
        )
        if document:
            extracted = str(getattr(document, "text", "") or "")
            title = _metadata_value(document, "title", default=title)
            author = _metadata_value(document, "author", default=author)
            publication_date = _metadata_value(document, "date", default=publication_date)
            extractor = "Trafilatura"
    except Exception:
        extracted = ""

    if word_count(extracted) < 40:
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response_text, "html.parser")
            for tag in soup(["script", "style", "nav", "aside", "footer", "form"]):
                tag.decompose()
            candidates = soup.select("article p") or soup.select("main p") or soup.find_all("p")
            extracted = "\n".join(paragraph.get_text(" ", strip=True) for paragraph in candidates)
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            author_node = soup.find("meta", attrs={"name": "author"})
            if author_node and author_node.get("content"):
                author = str(author_node["content"]).strip()
            date_node = soup.find("meta", attrs={"property": "article:published_time"})
            if date_node and date_node.get("content"):
                publication_date = str(date_node["content"]).strip()
            extractor = "BeautifulSoup fallback"
        except Exception as exc:
            raise ArticleExtractionError("No readable article body could be extracted.") from exc

    extracted = clean_article_text(extracted, remove_source_markers=False)
    count = word_count(extracted)
    if count < 40:
        raise ArticleExtractionError(
            "The page returned too little article text. Try pasting the article text directly."
        )
    return ArticleData(
        text=extracted,
        title=title,
        author=author,
        publication_date=publication_date,
        source_url=final_url,
        source_domain=domain_from_url(final_url),
        extractor=extractor,
        word_count=count,
        reading_time_minutes=reading_time_minutes(extracted),
    )
