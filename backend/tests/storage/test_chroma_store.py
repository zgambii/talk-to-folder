from pathlib import Path

import pytest

from app.core.config import Settings
from app.domain.documents.models import DocumentChunk
from app.storage.chroma_store import ChromaVectorStore, VectorStoreError


def test_chroma_vector_store_upserts_and_searches_chunks(tmp_path: Path) -> None:
    store = _store(tmp_path)
    chunks = [
        _chunk(id="chunk-1", folder_id="folder-1", text="alpha content", chunk_index=0),
        _chunk(id="chunk-2", folder_id="folder-1", text="beta content", chunk_index=1),
        _chunk(id="chunk-3", folder_id="folder-2", text="other folder", chunk_index=0),
    ]

    store.upsert_chunks(
        chunks=chunks,
        embeddings=[[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]],
    )

    results = store.search("folder-1", query_embedding=[1.0, 0.0], limit=2)

    assert [result.chunk_id for result in results] == ["chunk-1", "chunk-2"]
    assert all(result.score is not None for result in results)


def test_chroma_vector_store_round_trips_metadata(tmp_path: Path) -> None:
    store = _store(tmp_path)
    chunk = _chunk(
        id="chunk-1",
        folder_id="folder-1",
        document_id="document-1",
        drive_file_id="drive-file-1",
        document_name="Design notes",
        source_url="https://drive.google.com/file",
        chunk_index=7,
        text="alpha content",
    )

    store.upsert_chunks([chunk], [[1.0, 0.0]])

    result = store.search("folder-1", query_embedding=[1.0, 0.0], limit=1)[0]

    assert result.document_id == "document-1"
    assert result.document_name == "Design notes"
    assert result.source_url == "https://drive.google.com/file"
    assert result.chunk_index == 7
    assert result.text == "alpha content"


def test_chroma_vector_store_delete_folder_removes_folder_chunks(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    store.upsert_chunks(
        [
            _chunk(id="chunk-1", folder_id="folder-1", text="alpha"),
            _chunk(id="chunk-2", folder_id="folder-2", text="beta"),
        ],
        [[1.0, 0.0], [0.0, 1.0]],
    )

    store.delete_folder("folder-1")

    assert store.search("folder-1", query_embedding=[1.0, 0.0]) == []
    assert [result.chunk_id for result in store.search("folder-2", [0.0, 1.0])] == [
        "chunk-2"
    ]


def test_chroma_vector_store_rejects_mismatched_chunks_and_embeddings(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)

    with pytest.raises(VectorStoreError) as exc_info:
        store.upsert_chunks([_chunk(id="chunk-1")], [])

    assert str(exc_info.value) == "chunks and embeddings must have the same length."


def _store(tmp_path: Path) -> ChromaVectorStore:
    return ChromaVectorStore(
        settings=Settings(
            openai_api_key=None,
            openai_embedding_model="text-embedding-3-small",
            openai_answer_model="gpt-4.1-mini",
            chroma_path=str(tmp_path / "chroma"),
            frontend_origin="http://localhost:5173",
            app_env="test",
            google_client_id="test-client-id",
            google_client_secret="test-client-secret",
            google_redirect_uri="http://localhost:8000/api/auth/google/callback",
            frontend_url="http://localhost:5173",
            session_secret_key="test-session-secret",
        )
    )


def _chunk(
    id: str,
    folder_id: str = "folder-1",
    document_id: str = "document-1",
    drive_file_id: str = "drive-file-1",
    document_name: str = "Document",
    source_url: str | None = None,
    chunk_index: int = 0,
    text: str = "chunk text",
) -> DocumentChunk:
    return DocumentChunk(
        id=id,
        folder_id=folder_id,
        document_id=document_id,
        drive_file_id=drive_file_id,
        document_name=document_name,
        source_url=source_url,
        chunk_index=chunk_index,
        text=text,
    )
