from enum import StrEnum

from pydantic import BaseModel


# Document models describe source files and chunks created during indexing.
class SupportedFileType(StrEnum):
    GOOGLE_DOC = "google_doc"
    PDF = "pdf"
    TEXT = "text"
    MARKDOWN = "markdown"


class DriveFile(BaseModel):
    id: str
    name: str
    mime_type: str
    web_url: str | None = None
    created_time: str | None = None
    modified_time: str | None = None


class SkippedFile(BaseModel):
    file_id: str
    name: str
    mime_type: str | None = None
    reason: str


class SourceDocument(BaseModel):
    id: str
    drive_file_id: str
    name: str
    mime_type: str
    source_url: str | None = None
    text: str
    created_time: str | None = None
    modified_time: str | None = None


class DocumentChunk(BaseModel):
    id: str
    folder_id: str
    document_id: str
    drive_file_id: str
    document_name: str
    source_url: str | None = None
    chunk_index: int
    text: str
