"""TXT/PDF upload validation tests."""

import pytest

from src.file_parser import FileParseError, parse_uploaded_file, safe_upload_filename


def test_txt_file_upload(sample_article: str) -> None:
    parsed = parse_uploaded_file("article.txt", sample_article.encode("utf-8"))
    assert parsed.startswith("City engineers")


@pytest.mark.parametrize("filename,data", [("empty.txt", b""), ("image.png", b"not an article")])
def test_bad_uploads_are_rejected(filename: str, data: bytes) -> None:
    with pytest.raises(FileParseError):
        parse_uploaded_file(filename, data)


@pytest.mark.parametrize(
    "filename",
    ["../article.txt", "folder/article.txt", r"C:\\temp\\article.txt", ".."],
)
def test_upload_filename_traversal_is_rejected(filename: str) -> None:
    with pytest.raises(FileParseError, match="filename"):
        safe_upload_filename(filename)
