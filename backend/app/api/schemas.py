from typing import Literal

from pydantic import BaseModel

from app.ai.models import Citation, RetrievedChunk
from app.domain.documents.models import SkippedFile


class IndexFolderRequest(BaseModel):
    folder_url: str


class IndexFolderResponse(BaseModel):
    folder_id: str
    folder_url: str
    name: str | None = None
    files_found: int
    files_indexed: int
    chunks_created: int
    skipped_files: list[SkippedFile]


class ChatRequest(BaseModel):
    folder_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
