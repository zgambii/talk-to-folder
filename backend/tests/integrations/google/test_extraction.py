from io import BytesIO

import pytest
from googleapiclient.errors import Error as GoogleApiError

from app.domain.documents.models import DriveFile, SourceDocument
from app.integrations.google import extraction
from app.integrations.google.extraction import (
    DocumentExtractionError,
    GoogleDriveExtractor,
    UnsupportedFileTypeError,
    bytes_to_text,
)


class FakeMediaRequest:
    def __init__(self, content: bytes | Exception) -> None:
        self.content = content


class FakeFilesResource:
    def __init__(self, content: bytes | Exception) -> None:
        self.content = content
        self.export_media_calls: list[dict[str, str]] = []
        self.get_media_calls: list[dict[str, str]] = []

    def export_media(self, **kwargs: str) -> FakeMediaRequest:
        self.export_media_calls.append(kwargs)
        return FakeMediaRequest(self.content)

    def get_media(self, **kwargs: str) -> FakeMediaRequest:
        self.get_media_calls.append(kwargs)
        return FakeMediaRequest(self.content)


class FakeDriveService:
    def __init__(self, content: bytes | Exception) -> None:
        self.files_resource = FakeFilesResource(content)

    def files(self) -> FakeFilesResource:
        return self.files_resource


class FakeDownloader:
    def __init__(self, buffer: BytesIO, request: FakeMediaRequest) -> None:
        self._buffer = buffer
        self._request = request

    def next_chunk(self) -> tuple[None, bool]:
        if isinstance(self._request.content, Exception):
            raise self._request.content

        self._buffer.write(self._request.content)
        return None, True


def test_extract_text_exports_google_doc_as_plain_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(extraction, "MediaIoBaseDownload", FakeDownloader)
    service = FakeDriveService(b"Project notes")
    client = _client_with_service(service)
    file = DriveFile(
        id="doc-1",
        name="Project notes",
        mime_type="application/vnd.google-apps.document",
        web_url="https://drive.google.com/doc-1",
        created_time="2026-01-01T00:00:00Z",
        modified_time="2026-01-02T00:00:00Z",
    )

    document = client.extract_text(file)

    assert document == SourceDocument(
        id="doc-1",
        drive_file_id="doc-1",
        name="Project notes",
        mime_type="application/vnd.google-apps.document",
        source_url="https://drive.google.com/doc-1",
        text="Project notes",
        created_time="2026-01-01T00:00:00Z",
        modified_time="2026-01-02T00:00:00Z",
    )
    assert service.files_resource.export_media_calls == [
        {"fileId": "doc-1", "mimeType": "text/plain"}
    ]


@pytest.mark.parametrize(
    ("file", "content"),
    [
        (
            DriveFile(id="text-1", name="notes.txt", mime_type="text/plain"),
            b"Plain text",
        ),
        (
            DriveFile(
                id="markdown-1",
                name="README.md",
                mime_type="application/octet-stream",
            ),
            b"# Heading",
        ),
    ],
)
def test_extract_text_downloads_text_and_markdown_files(
    monkeypatch: pytest.MonkeyPatch,
    file: DriveFile,
    content: bytes,
) -> None:
    monkeypatch.setattr(extraction, "MediaIoBaseDownload", FakeDownloader)
    service = FakeDriveService(content)
    client = _client_with_service(service)

    document = client.extract_text(file)

    assert document.text == content.decode("utf-8")
    assert document.drive_file_id == file.id
    assert document.source_url == file.web_url
    assert service.files_resource.get_media_calls == [{"fileId": file.id}]


def test_extract_text_uses_pdf_extraction_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(extraction, "MediaIoBaseDownload", FakeDownloader)
    monkeypatch.setattr(extraction, "extract_pdf_text", lambda content: "PDF text")
    service = FakeDriveService(b"pdf bytes")
    client = _client_with_service(service)
    file = DriveFile(id="pdf-1", name="Spec.pdf", mime_type="application/pdf")

    document = client.extract_text(file)

    assert document.text == "PDF text"
    assert service.files_resource.get_media_calls == [{"fileId": "pdf-1"}]


def test_extract_text_rejects_unsupported_files() -> None:
    client = _client_with_service(FakeDriveService(b"image bytes"))
    file = DriveFile(id="image-1", name="diagram.png", mime_type="image/png")

    with pytest.raises(UnsupportedFileTypeError):
        client.extract_text(file)


def test_extract_text_wraps_google_download_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(extraction, "MediaIoBaseDownload", FakeDownloader)
    service = FakeDriveService(GoogleApiError("download failed"))
    client = _client_with_service(service)
    file = DriveFile(id="text-1", name="notes.txt", mime_type="text/plain")

    with pytest.raises(DocumentExtractionError) as exc_info:
        client.extract_text(file)

    assert str(exc_info.value) == "Could not download the document from Google Drive."
    assert isinstance(exc_info.value.__cause__, GoogleApiError)


def test_extract_text_wraps_extraction_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(extraction, "MediaIoBaseDownload", FakeDownloader)

    def raise_pdf_error(content: bytes) -> str:
        raise ValueError("bad pdf")

    monkeypatch.setattr(extraction, "extract_pdf_text", raise_pdf_error)
    client = _client_with_service(FakeDriveService(b"pdf bytes"))
    file = DriveFile(id="pdf-1", name="Spec.pdf", mime_type="application/pdf")

    with pytest.raises(DocumentExtractionError) as exc_info:
        client.extract_text(file)

    assert str(exc_info.value) == "Could not extract text from the document."
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_bytes_to_text_replaces_invalid_utf8_bytes() -> None:
    assert bytes_to_text(b"valid \xff text") == "valid \ufffd text"


def _client_with_service(service: FakeDriveService) -> GoogleDriveExtractor:
    client = GoogleDriveExtractor.__new__(GoogleDriveExtractor)
    client._service = service
    return client
