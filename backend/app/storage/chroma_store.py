from typing import Any

import chromadb

from app.ai.models import RetrievedChunk
from app.core.config import Settings, get_settings
from app.domain.documents.models import DocumentChunk

COLLECTION_NAME = "document_chunks"


class VectorStoreError(ValueError):
    """Raised when vector store input is invalid."""


class ChromaVectorStore:
    """Persistent Chroma-backed implementation of the vector store interface."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Open or create the local Chroma collection at the configured path."""

        self._settings = settings or get_settings()
        self._client = chromadb.PersistentClient(path=self._settings.chroma_path)
        self._collection = self._client.get_or_create_collection(name=COLLECTION_NAME)

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Store chunks with matching embeddings and searchable metadata."""

        if len(chunks) != len(embeddings):
            raise VectorStoreError("chunks and embeddings must have the same length.")

        if not chunks:
            return

        self._collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[_metadata_from_chunk(chunk) for chunk in chunks],
        )

    def search(
        self,
        folder_id: str,
        query_embedding: list[float],
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        """Search only within one folder and return app-level retrieval models."""

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where={"folder_id": folder_id},
        )

        ids = _first_result_list(results.get("ids"))
        documents = _first_result_list(results.get("documents"))
        metadatas = _first_result_list(results.get("metadatas"))
        distances = _first_result_list(results.get("distances"))

        retrieved_chunks: list[RetrievedChunk] = []
        for index, chunk_id in enumerate(ids):
            metadata = metadatas[index]
            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=str(chunk_id),
                    document_id=str(metadata["document_id"]),
                    document_name=str(metadata["document_name"]),
                    source_url=_optional_metadata_value(metadata.get("source_url")),
                    chunk_index=int(metadata["chunk_index"]),
                    text=str(documents[index]),
                    score=_optional_score(distances, index),
                )
            )

        return retrieved_chunks

    def delete_folder(self, folder_id: str) -> None:
        """Remove all chunks associated with a folder from Chroma."""

        self._collection.delete(where={"folder_id": folder_id})


def _metadata_from_chunk(chunk: DocumentChunk) -> dict[str, str | int]:
    """Convert chunk fields into Chroma metadata primitives."""

    return {
        "folder_id": chunk.folder_id,
        "document_id": chunk.document_id,
        "drive_file_id": chunk.drive_file_id,
        "document_name": chunk.document_name,
        "source_url": chunk.source_url or "",
        "chunk_index": chunk.chunk_index,
    }


def _first_result_list(value: Any) -> list[Any]:
    """Unwrap Chroma's single-query nested result lists."""

    if not value:
        return []

    return list(value[0])


def _optional_metadata_value(value: Any) -> str | None:
    """Convert Chroma's stored empty-string sentinel back to None."""

    if value is None or value == "":
        return None

    return str(value)


def _optional_score(distances: list[Any], index: int) -> float | None:
    """Return Chroma's distance score when it is present."""

    if index >= len(distances):
        return None

    return float(distances[index])
