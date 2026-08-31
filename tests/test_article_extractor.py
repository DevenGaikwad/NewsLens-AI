"""Safe URL checks, redirect controls, bounded downloads and extraction fallbacks."""

from types import SimpleNamespace

import pytest

from src.article_extractor import (
    ArticleExtractionError,
    _download_public_html,
    _validate_public_url,
    extract_article,
)
from src.config import MAX_ARTICLE_RESPONSE_BYTES


PUBLIC_DNS = [(None, None, None, None, ("93.184.216.34", 443))]


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        text: str = "<html></html>",
        headers: dict[str, str] | None = None,
        peer: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.text = text
        self.headers = headers or {"content-type": "text/html"}
        self.encoding = "utf-8"
        self.closed = False
        if peer:
            sock = SimpleNamespace(getpeername=lambda: (peer, 443))
            self.raw = SimpleNamespace(_connection=SimpleNamespace(sock=sock))
        else:
            self.raw = None

    def iter_content(self, chunk_size: int):
        del chunk_size
        yield self.text.encode("utf-8")

    def raise_for_status(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.requests: list[str] = []
        self.trust_env = True

    def get(self, url: str, **kwargs) -> FakeResponse:
        assert kwargs["allow_redirects"] is False
        assert kwargs["stream"] is True
        self.requests.append(url)
        return self.responses.pop(0)

    def close(self) -> None:
        return None


def use_fake_session(monkeypatch, responses: list[FakeResponse]) -> FakeSession:
    session = FakeSession(responses)
    monkeypatch.setattr("requests.Session", lambda: session)
    return session


def test_rejects_invalid_private_and_obfuscated_urls(monkeypatch) -> None:
    with pytest.raises(ArticleExtractionError):
        _validate_public_url("not-a-url")
    with pytest.raises(ArticleExtractionError):
        _validate_public_url("http://localhost/admin")
    with pytest.raises(ArticleExtractionError):
        _validate_public_url("http://2130706433/admin")
    with pytest.raises(ArticleExtractionError):
        _validate_public_url("http://0177.0.0.1/admin")
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *_: [(None, None, None, None, ("127.0.0.1", 0))],
    )
    with pytest.raises(ArticleExtractionError, match="private"):
        _validate_public_url("https://example.test/story")


def test_public_redirect_to_private_address_is_blocked(monkeypatch) -> None:
    monkeypatch.setattr("socket.getaddrinfo", lambda *_: PUBLIC_DNS)
    session = use_fake_session(
        monkeypatch,
        [FakeResponse(status_code=302, headers={"location": "http://127.0.0.1/admin"})],
    )
    with pytest.raises(ArticleExtractionError, match="private"):
        _download_public_html("https://example.test/story")
    assert session.requests == ["https://example.test/story"]


def test_redirect_loop_is_blocked(monkeypatch) -> None:
    monkeypatch.setattr("socket.getaddrinfo", lambda *_: PUBLIC_DNS)
    use_fake_session(
        monkeypatch,
        [FakeResponse(status_code=302, headers={"location": "/story"})],
    )
    with pytest.raises(ArticleExtractionError, match="redirect loop"):
        _download_public_html("https://example.test/story")


def test_dns_peer_change_is_blocked_when_socket_is_available(monkeypatch) -> None:
    monkeypatch.setattr("socket.getaddrinfo", lambda *_: PUBLIC_DNS)
    use_fake_session(monkeypatch, [FakeResponse(peer="93.184.216.35")])
    with pytest.raises(ArticleExtractionError, match="changed"):
        _download_public_html("https://example.test/story")


def test_response_size_limit_is_enforced_before_body_read(monkeypatch) -> None:
    monkeypatch.setattr("socket.getaddrinfo", lambda *_: PUBLIC_DNS)
    use_fake_session(
        monkeypatch,
        [
            FakeResponse(
                headers={
                    "content-type": "text/html",
                    "content-length": str(MAX_ARTICLE_RESPONSE_BYTES + 1),
                }
            )
        ],
    )
    with pytest.raises(ArticleExtractionError, match="5 MB"):
        _download_public_html("https://example.test/story")


def test_extract_article_with_mocked_html(monkeypatch) -> None:
    paragraphs = "".join(
        f"<p>Paragraph {i} reports a documented public event with enough contextual words for reliable text extraction and analysis.</p>"
        for i in range(1, 7)
    )
    html = (
        "<html><head><title>Mock report</title><meta name='author' content='Test Author'>"
        f"</head><body><article>{paragraphs}</article></body></html>"
    )
    monkeypatch.setattr(
        "src.article_extractor._download_public_html",
        lambda *_: (html, "https://example.test/story", {"content-type": "text/html"}),
    )
    monkeypatch.setattr("trafilatura.bare_extraction", lambda *_, **__: None)
    article = extract_article("https://example.test/story")
    assert article.title == "Mock report"
    assert article.author == "Test Author"
    assert article.extractor == "BeautifulSoup fallback"
    assert article.word_count >= 40
