from typing import Any

from supabase import Client, create_client

from app.ai.models import RetrievedChunk
from app.core.config import Settings, get_settings
from app.domain.documents.models import DocumentChunk


class SupabaseVectorStoreError(RuntimeError):
    """Raised when Supabase vector storage cannot complete an operation."""


class SupabaseVectorStore:
    """Supabase pgvector-backed implementation of the vector store interface."""

    def __init__(
        self,
        settings: Settings | None = None,
        client: Client | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client or _create_supabase_client(self._settings)

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise SupabaseVectorStoreError(
                "chunks and embeddings must have the same length."
            )

        if not chunks:
            return

        rows = [
            _row_from_chunk(chunk=chunk, embedding=embedding)
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
        try:
            self._client.table("document_chunks").upsert(rows).execute()
        except Exception as exc:
            raise SupabaseVectorStoreError("Could not upsert document chunks.") from exc

    def search(
        self,
        folder_id: str,
        query_embedding: list[float],
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        try:
            response = self._client.rpc(
                "match_document_chunks",
                {
                    "query_embedding": query_embedding,
                    "match_folder_id": folder_id,
                    "match_count": limit,
                },
            ).execute()
        except Exception as exc:
            raise SupabaseVectorStoreError("Could not search document chunks.") from exc

        return [_retrieved_chunk_from_row(row) for row in response.data or []]

    def delete_folder(self, folder_id: str) -> None:
        try:
            (
                self._client.table("document_chunks")
                .delete()
                .eq("folder_id", folder_id)
                .execute()
            )
        except Exception as exc:
            raise SupabaseVectorStoreError("Could not delete document chunks.") from exc


def _create_supabase_client(settings: Settings) -> Client:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SupabaseVectorStoreError("Supabase vector store is not configured.")

    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def _row_from_chunk(
    chunk: DocumentChunk,
    embedding: list[float],
) -> dict[str, Any]:
    return {
        "id": chunk.id,
        "folder_id": chunk.folder_id,
        "document_id": chunk.document_id,
        "drive_file_id": chunk.drive_file_id,
        "document_name": chunk.document_name,
        "source_url": chunk.source_url,
        "chunk_index": chunk.chunk_index,
        "text": chunk.text,
        "embedding": embedding,
    }


def _retrieved_chunk_from_row(row: dict[str, Any]) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=str(row["id"]),
        document_id=str(row["document_id"]),
        document_name=str(row["document_name"]),
        source_url=row.get("source_url"),
        chunk_index=int(row["chunk_index"]),
        text=str(row["text"]),
        score=_optional_score(row.get("score")),
    )


def _optional_score(score: Any) -> float | None:
    if score is None:
        return None

    return float(score)
