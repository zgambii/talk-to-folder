import pytest

from app.domain.documents.file_types import get_supported_file_type
from app.domain.documents.models import SupportedFileType


@pytest.mark.parametrize(
    ("mime_type", "name", "expected_file_type"),
    [
        (
            "application/vnd.google-apps.document",
            "Project notes",
            SupportedFileType.GOOGLE_DOC,
        ),
        ("application/pdf", "Spec.pdf", SupportedFileType.PDF),
        ("text/plain", "notes.txt", SupportedFileType.TEXT),
        ("text/markdown", "notes", SupportedFileType.MARKDOWN),
        ("application/octet-stream", "README.md", SupportedFileType.MARKDOWN),
        ("application/octet-stream", "README.markdown", SupportedFileType.MARKDOWN),
    ],
)
def test_get_supported_file_type_returns_supported_type(
    mime_type: str,
    name: str,
    expected_file_type: SupportedFileType,
) -> None:
    assert get_supported_file_type(mime_type, name) == expected_file_type


def test_get_supported_file_type_returns_none_for_unsupported_file() -> None:
    assert get_supported_file_type("image/png", "diagram.png") is None
