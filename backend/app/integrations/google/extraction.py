from io import BytesIO

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import Error as GoogleApiError
from googleapiclient.http import MediaIoBaseDownload
from pypdf import PdfReader

from app.domain.documents.file_types import get_supported_file_type
from app.domain.documents.models import DriveFile, SourceDocument, SupportedFileType


class UnsupportedFileTypeError(ValueError):
    """Raised when a file cannot be extracted by the current backend."""


class DocumentExtractionError(RuntimeError):
    """Raised when supported document text extraction fails."""


class GoogleDriveExtractor:
    def __init__(self, access_token: str) -> None:
        credentials = Credentials(token=access_token)
        self._service = build("drive", "v3", credentials=credentials)

    def extract_text(self, file: DriveFile) -> SourceDocument:
        file_type = get_supported_file_type(file.mime_type, file.name)
        if file_type is None:
            raise UnsupportedFileTypeError(
                f"File type is not supported for extraction: {file.name}"
            )

        try:
            text = _extract_text_for_file_type(self._service, file, file_type)
        except GoogleApiError as exc:
            raise DocumentExtractionError(
                "Could not download the document from Google Drive."
            ) from exc
        except Exception as exc:
            raise DocumentExtractionError(
                "Could not extract text from the document."
            ) from exc

        return SourceDocument(
            id=file.id,
            drive_file_id=file.id,
            name=file.name,
            mime_type=file.mime_type,
            source_url=file.web_url,
            text=text,
            created_time=file.created_time,
            modified_time=file.modified_time,
        )


def _extract_text_for_file_type(
    service,
    file: DriveFile,
    file_type: SupportedFileType,
) -> str:
    if file_type == SupportedFileType.GOOGLE_DOC:
        return _export_google_doc_as_text(service, file.id)

    file_bytes = _download_file_bytes(service, file.id)
    if file_type == SupportedFileType.PDF:
        return extract_pdf_text(file_bytes)

    return bytes_to_text(file_bytes)


def _export_google_doc_as_text(service, file_id: str) -> str:
    request = service.files().export_media(fileId=file_id, mimeType="text/plain")
    return bytes_to_text(_download_request_bytes(request))


def _download_file_bytes(service, file_id: str) -> bytes:
    request = service.files().get_media(fileId=file_id)
    return _download_request_bytes(request)


def _download_request_bytes(request) -> bytes:
    buffer = BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False

    while not done:
        _, done = downloader.next_chunk()

    return buffer.getvalue()


def bytes_to_text(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    page_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text for text in page_text if text)
