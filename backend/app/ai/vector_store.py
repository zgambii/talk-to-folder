from typing import Protocol

from app.ai.models import RetrievedChunk
from app.domain.documents.models import DocumentChunk


class VectorStore(Protocol):
    """Interface for storing and retrieving embedded document chunks.

    Implementations can use Chroma locally, pgvector in production, or any
    other vector database without changing the RAG pipeline.
    """

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Insert or update chunks and their embeddings."""
        ...

    def search(
        self,
        folder_id: str,
        query_embedding: list[float],
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        """Return the most relevant chunks for a folder-scoped query."""
        ...

    def delete_folder(self, folder_id: str) -> None:
        """Delete all indexed chunks for a folder."""
        ...
