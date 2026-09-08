"""Safe URL validation and layered news-article extraction."""

from __future__ import annotations

import ipaddress
import re
import socket
import sys
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


def _public_unicast_address(value: str) -> str:
    """Return a canonical public-unicast address or reject it fail closed."""

    if "%" in value:
        raise ArticleExtractionError("Scoped network addresses are not supported.")
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ArticleExtractionError("The website resolved to an invalid network address.") from exc
    mapped = getattr(address, "ipv4_mapped", None)
    effective = mapped or address
    if (
        not effective.is_global
        or effective.is_loopback
        or effective.is_private
        or effective.is_link_local
        or effective.is_multicast
        or effective.is_reserved
        or effective.is_unspecified
    ):
        raise ArticleExtractionError("Local or private network URLs are blocked.")
    return str(address)


def _resolved_public_addresses(hostname: str, port: int) -> tuple[str, ...]:
    """Resolve a host and fail closed unless every answer is globally routable."""

    try:
        records = socket.getaddrinfo(hostname, port, 0, socket.SOCK_STREAM)
    except (socket.gaierror, OSError) as exc:
        raise ArticleExtractionError("The website hostname could not be resolved.") from exc
    addresses: list[str] = []
    for family, _, _, _, sockaddr in records:
        if family not in {socket.AF_INET, socket.AF_INET6} or not sockaddr:
            raise ArticleExtractionError("The website resolved to an invalid network address.")
        address = _public_unicast_address(str(sockaddr[0]))
        if address not in addresses:
            addresses.append(address)
    if not addresses:
        raise ArticleExtractionError("The website hostname could not be resolved.")
    return tuple(addresses)


def _validate_public_target(url: str) -> tuple[str, tuple[str, ...]]:
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
        addresses = (_public_unicast_address(str(literal)),)
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


def _bound_adapter(requests: Any, hostname: str, approved_address: str) -> Any:
    """Create an isolated adapter whose socket can connect only to one vetted IP."""

    from urllib3 import PoolManager
    from urllib3.connection import HTTPConnection, HTTPSConnection
    from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
    from urllib3.util import connection

    def verify_peer(sock: Any) -> None:
        try:
            peer = _public_unicast_address(str(sock.getpeername()[0]))
        except (AttributeError, OSError, TypeError, ArticleExtractionError) as exc:
            raise OSError("The remote server address could not be verified.") from exc
        if peer != approved_address:
            raise OSError("The remote server address changed during validation.")

    class BoundHTTPConnection(HTTPConnection):
        def _new_conn(self) -> socket.socket:
            sock = connection.create_connection(
                (approved_address, self.port),
                self.timeout,
                source_address=self.source_address,
                socket_options=self.socket_options,
            )
            verify_peer(sock)
            sys.audit("http.client.connect", self, self.host, self.port)
            return sock

    class BoundHTTPSConnection(HTTPSConnection):
        def _new_conn(self) -> socket.socket:
            sock = connection.create_connection(
                (approved_address, self.port),
                self.timeout,
                source_address=self.source_address,
                socket_options=self.socket_options,
            )
            verify_peer(sock)
            sys.audit("http.client.connect", self, self.host, self.port)
            return sock

    class BoundHTTPPool(HTTPConnectionPool):
        ConnectionCls = BoundHTTPConnection

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs.pop("server_hostname", None)
            kwargs.pop("assert_hostname", None)
            super().__init__(*args, **kwargs)

    class BoundHTTPSPool(HTTPSConnectionPool):
        ConnectionCls = BoundHTTPSConnection

    class BoundAdapter(requests.adapters.HTTPAdapter):
        def init_poolmanager(self, connections: int, maxsize: int, block: bool = False, **kwargs: Any) -> None:
            manager = PoolManager(
                num_pools=1,
                maxsize=1,
                block=True,
                server_hostname=hostname,
                assert_hostname=hostname,
                **kwargs,
            )
            manager.pool_classes_by_scheme = {"http": BoundHTTPPool, "https": BoundHTTPSPool}
            self.poolmanager = manager

    adapter = BoundAdapter(pool_connections=1, pool_maxsize=1, max_retries=0, pool_block=True)
    adapter._approved_address = approved_address
    adapter._original_hostname = hostname
    return adapter


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
    current = url
    visited: set[str] = set()
    for redirect_number in range(MAX_REDIRECTS + 1):
        safe_url, resolved = _validate_public_target(current)
        if safe_url in visited:
            raise ArticleExtractionError("The article URL contains a redirect loop.")
        visited.add(safe_url)
        parsed = urlparse(safe_url)
        hostname = (parsed.hostname or "").rstrip(".").encode("idna").decode("ascii").lower()
        host_header = f"[{hostname}]" if ":" in hostname else hostname
        if parsed.port is not None:
            host_header = f"{host_header}:{parsed.port}"
        last_error: Exception | None = None
        response = None
        for address in resolved:
            session = requests.Session()
            session.trust_env = False
            session.mount("http://", _bound_adapter(requests, hostname, address))
            session.mount("https://", _bound_adapter(requests, hostname, address))
            try:
                ip_netloc = f"[{address}]" if ":" in address else address
                if parsed.port is not None:
                    ip_netloc = f"{ip_netloc}:{parsed.port}"
                bound_url = parsed._replace(netloc=ip_netloc).geturl()
                response = session.get(
                    bound_url,
                    headers={**headers, "Host": host_header},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    allow_redirects=False,
                    stream=True,
                )
            except requests.RequestException as exc:
                last_error = exc
                session.close()
                continue
            break
        if response is None:
            raise ArticleExtractionError(
                "The article could not be downloaded. The site may be unavailable, "
                "paywalled, or blocking automated extraction."
            ) from last_error
        try:
            if response.status_code in REDIRECT_STATUSES:
                location = response.headers.get("location")
                if not location:
                    raise ArticleExtractionError("The website returned an invalid redirect.")
                if redirect_number >= MAX_REDIRECTS:
                    raise ArticleExtractionError("The article URL exceeded the redirect limit.")
                current = urljoin(safe_url, location)
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
            response.close()
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
