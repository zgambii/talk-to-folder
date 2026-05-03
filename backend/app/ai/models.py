from typing import Literal

from pydantic import BaseModel


# AI models define retrieval context, citations, and generated answer payloads.
class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    source_url: str | None = None
    chunk_index: int
    text: str
    score: float | None = None


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    source_url: str | None = None
    quote: str


class FolderAnswer(BaseModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    citations: list[Citation]
