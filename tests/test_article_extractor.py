"""Deterministic SSRF, redirect, bounded-download and extraction tests."""

import socket
from types import SimpleNamespace

import pytest
import requests

from src.article_extractor import (
    ArticleExtractionError, _bound_adapter, _download_public_html,
    _resolved_public_addresses, _validate_public_url, extract_article,
)
from src.config import MAX_ARTICLE_RESPONSE_BYTES, MAX_REDIRECTS, REQUEST_TIMEOUT_SECONDS

PUBLIC_V4 = "93.184.216.34"
PUBLIC_V6 = "2606:2800:220:1:248:1893:25c8:1946"


def dns(*addresses: str):
    return [(socket.AF_INET6 if ":" in a else socket.AF_INET, socket.SOCK_STREAM,
             socket.IPPROTO_TCP, "", (a, 443, 0, 0) if ":" in a else (a, 443))
            for a in addresses]


class FakeResponse:
    def __init__(self, *, status_code=200, text="<html></html>", headers=None):
        self.status_code, self.text = status_code, text
        self.headers = headers or {"content-type": "text/html"}
        self.encoding, self.closed = "utf-8", False

    def iter_content(self, chunk_size):
        del chunk_size
        yield self.text.encode()

    def raise_for_status(self):
        return None

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, responses):
        self.responses, self.requests, self.mounts = responses, [], {}
        self.trust_env, self.closed = True, False

    def mount(self, prefix, adapter):
        self.mounts[prefix] = adapter

    def get(self, url, **kwargs):
        self.requests.append((url, kwargs, dict(self.mounts)))
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def close(self):
        self.closed = True


def session_factory(monkeypatch, responses):
    sessions = []
    def make_session():
        item = FakeSession(responses)
        sessions.append(item)
        return item
    monkeypatch.setattr("requests.Session", make_session)
    return sessions


@pytest.mark.parametrize("address", [PUBLIC_V4, PUBLIC_V6])
def test_public_unicast_dns_answers_are_accepted(monkeypatch, address):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(address))
    assert _resolved_public_addresses("example.test", 443) == (address,)


@pytest.mark.parametrize("address", [
    "127.0.0.1", "::1", "10.0.0.1", "fc00::1", "169.254.1.1", "fe80::1",
    "224.0.0.1", "ff02::1", "240.0.0.1", "::", "100.64.0.1",
    "::ffff:127.0.0.1", "169.254.169.254", "fe80::1%eth0",
])
def test_non_public_or_scoped_dns_answers_are_rejected(monkeypatch, address):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(address))
    with pytest.raises(ArticleExtractionError):
        _resolved_public_addresses("example.test", 443)


def test_mixed_dns_answers_fail_closed(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(PUBLIC_V4, "127.0.0.1"))
    with pytest.raises(ArticleExtractionError, match="private"):
        _validate_public_url("https://example.test/story")


@pytest.mark.parametrize("url", [
    "not-a-url", "file:///etc/passwd", "ftp://example.test/a", "gopher://example.test/a",
    "http://user:secret" + chr(64) + "example.test/", "http://localhost/admin", "http://2130706433/",
    "http://0x7f000001/", "http://0177.0.0.1/", "http://0x7f.0.0.1/",
    "http://127.1/", "http://[fe80::1%25eth0]/",
])
def test_prohibited_schemes_credentials_and_numeric_forms_are_rejected(url):
    with pytest.raises(ArticleExtractionError):
        _validate_public_url(url)


def test_bound_adapter_uses_only_approved_ip_and_preserves_hostname(monkeypatch):
    calls = []
    sock = SimpleNamespace(getpeername=lambda: (PUBLIC_V4, 443))
    monkeypatch.setattr("urllib3.util.connection.create_connection",
                        lambda target, *_a, **_k: calls.append(target) or sock)
    adapter = _bound_adapter(requests, "example.test", PUBLIC_V4)
    pool = adapter.poolmanager.connection_from_url(f"https://{PUBLIC_V4}/story")
    connection = pool._new_conn()
    connection._new_conn()
    assert calls == [(PUBLIC_V4, 443)]
    assert connection.host == PUBLIC_V4
    assert connection.server_hostname == "example.test"
    assert connection.assert_hostname == "example.test"
    assert adapter._original_hostname == "example.test"


@pytest.mark.parametrize("peer", ["93.184.216.35", None])
def test_peer_mismatch_or_missing_identity_fails_before_http_data(monkeypatch, peer):
    class Socket:
        def getpeername(self):
            if peer is None:
                raise OSError("unavailable")
            return (peer, 443)
    monkeypatch.setattr("urllib3.util.connection.create_connection", lambda *_a, **_k: Socket())
    adapter = _bound_adapter(requests, "example.test", PUBLIC_V4)
    pool = adapter.poolmanager.connection_from_url("http://example.test/story")
    with pytest.raises(OSError):
        pool.ConnectionCls("example.test", 80)._new_conn()


def test_dns_rebinding_second_lookup_cannot_choose_connection(monkeypatch):
    lookups, targets = [], []
    def lookup(*_):
        lookups.append(True)
        return dns(PUBLIC_V4) if len(lookups) == 1 else dns("127.0.0.1")
    monkeypatch.setattr(socket, "getaddrinfo", lookup)
    sock = SimpleNamespace(getpeername=lambda: (PUBLIC_V4, 443))
    monkeypatch.setattr("urllib3.util.connection.create_connection",
                        lambda target, *_a, **_k: targets.append(target) or sock)
    assert _resolved_public_addresses("example.test", 443) == (PUBLIC_V4,)
    adapter = _bound_adapter(requests, "example.test", PUBLIC_V4)
    pool = adapter.poolmanager.connection_from_url(f"https://{PUBLIC_V4}/")
    pool._new_conn()._new_conn()
    assert len(lookups) == 1 and targets == [(PUBLIC_V4, 443)]


def test_multiple_addresses_retry_in_vetted_order_without_pool_reuse(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(PUBLIC_V4, PUBLIC_V6))
    sessions = session_factory(monkeypatch, [requests.ConnectionError("failed"), FakeResponse(text="ok")])
    assert _download_public_html("https://example.test/story")[0] == "ok"
    assert [s.mounts["https://"]._approved_address for s in sessions] == [PUBLIC_V4, PUBLIC_V6]
    assert sessions[0] is not sessions[1]


def test_host_timeout_tls_verification_and_proxy_controls(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(PUBLIC_V4))
    sessions = session_factory(monkeypatch, [FakeResponse(text="ok")])
    _download_public_html("https://example.test:8443/story")
    url, kwargs, mounts = sessions[0].requests[0]
    assert url == f"https://{PUBLIC_V4}:8443/story"
    assert kwargs["headers"]["Host"] == "example.test:8443"
    assert kwargs["timeout"] == REQUEST_TIMEOUT_SECONDS
    assert kwargs["allow_redirects"] is False and kwargs["stream"] is True
    assert "verify" not in kwargs  # Requests defaults preserve CA/hostname verification.
    assert mounts["https://"]._original_hostname == "example.test"
    assert sessions[0].trust_env is False


@pytest.mark.parametrize("target", ["http://127.0.0.1/admin", "http://224.0.0.1/admin"])
def test_private_or_multicast_redirect_is_blocked_before_second_request(monkeypatch, target):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(PUBLIC_V4))
    sessions = session_factory(monkeypatch, [FakeResponse(status_code=302, headers={"location": target})])
    with pytest.raises(ArticleExtractionError):
        _download_public_html("https://example.test/story")
    assert sum(len(s.requests) for s in sessions) == 1


def test_safe_redirect_is_freshly_resolved_and_bound(monkeypatch):
    answers = iter([dns(PUBLIC_V4), dns(PUBLIC_V6)])
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: next(answers))
    sessions = session_factory(monkeypatch, [
        FakeResponse(status_code=302, headers={"location": "https://other.test/new"}),
        FakeResponse(text="ok"),
    ])
    assert _download_public_html("https://example.test/story")[0] == "ok"
    assert sessions[0].mounts["https://"]._approved_address == PUBLIC_V4
    assert sessions[1].mounts["https://"]._approved_address == PUBLIC_V6
    assert sessions[1].requests[0][1]["headers"]["Host"] == "other.test"


def test_redirect_loop_and_limit_remain_enforced(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(PUBLIC_V4))
    session_factory(monkeypatch, [FakeResponse(status_code=302, headers={"location": "/story"})])
    with pytest.raises(ArticleExtractionError, match="redirect loop"):
        _download_public_html("https://example.test/story")
    responses = [FakeResponse(status_code=302, headers={"location": f"/r{i}"})
                 for i in range(MAX_REDIRECTS + 1)]
    session_factory(monkeypatch, responses)
    with pytest.raises(ArticleExtractionError, match="redirect limit"):
        _download_public_html("https://example.test/start")


def test_size_limit_and_sanitized_network_error(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_: dns(PUBLIC_V4))
    session_factory(monkeypatch, [FakeResponse(headers={"content-type": "text/html",
        "content-length": str(MAX_ARTICLE_RESPONSE_BYTES + 1)})])
    with pytest.raises(ArticleExtractionError, match="5 MB"):
        _download_public_html("https://example.test/story")
    sentinel = "SECRET_INTERNAL_DETAIL"
    session_factory(monkeypatch, [requests.ConnectionError(sentinel)])
    with pytest.raises(ArticleExtractionError) as error:
        _download_public_html("https://example.test/story")
    assert sentinel not in str(error.value)


def test_non_html_content_is_rejected(monkeypatch):
    monkeypatch.setattr("src.article_extractor._download_public_html",
        lambda *_: ("plain content", "https://example.test/story", {"content-type": "text/plain"}))
    with pytest.raises(ArticleExtractionError, match="HTML"):
        extract_article("https://example.test/story")


def test_extract_article_with_mocked_html(monkeypatch):
    paragraphs = "".join(f"<p>Paragraph {i} reports a documented public event with enough contextual words for reliable text extraction and analysis.</p>" for i in range(1, 7))
    html = f"<html><head><title>Mock report</title><meta name='author' content='Test Author'></head><body><article>{paragraphs}</article></body></html>"
    monkeypatch.setattr("src.article_extractor._download_public_html",
        lambda *_: (html, "https://example.test/story", {"content-type": "text/html"}))
    monkeypatch.setattr("trafilatura.bare_extraction", lambda *_, **__: None)
    article = extract_article("https://example.test/story")
    assert article.title == "Mock report" and article.author == "Test Author"
    assert article.extractor == "BeautifulSoup fallback" and article.word_count >= 40
