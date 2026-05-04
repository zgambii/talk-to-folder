import pytest

from app.domain.documents.models import DocumentChunk
from app.storage.supabase_vector_store import (
    SupabaseVectorStore,
    SupabaseVectorStoreError,
)


class FakeExecuteResponse:
    def __init__(self, data=None) -> None:
        self.data = data


class FakeTableQuery:
    def __init__(self, table_name: str, client: "FakeSupabaseClient") -> None:
        self.table_name = table_name
        self.client = client

    def upsert(self, rows):
        self.client.upsert_calls.append({"table": self.table_name, "rows": rows})
        return self

    def delete(self):
        self.client.delete_calls.append({"table": self.table_name})
        return self

    def eq(self, column: str, value: str):
        self.client.eq_calls.append({"column": column, "value": value})
        return self

    def execute(self):
        return FakeExecuteResponse()


class FakeRpcQuery:
    def __init__(self, client: "FakeSupabaseClient", rows) -> None:
        self.client = client
        self.rows = rows

    def execute(self):
        return FakeExecuteResponse(data=self.rows)


class FakeSupabaseClient:
    def __init__(self, rpc_rows=None) -> None:
        self.rpc_rows = rpc_rows or []
        self.upsert_calls: list[dict] = []
        self.delete_calls: list[dict] = []
        self.eq_calls: list[dict] = []
        self.rpc_calls: list[dict] = []

    def table(self, table_name: str) -> FakeTableQuery:
        return FakeTableQuery(table_name=table_name, client=self)

    def rpc(self, function_name: str, params: dict) -> FakeRpcQuery:
        self.rpc_calls.append({"function_name": function_name, "params": params})
        return FakeRpcQuery(client=self, rows=self.rpc_rows)


def test_supabase_vector_store_rejects_mismatched_chunks_and_embeddings() -> None:
    store = SupabaseVectorStore(client=FakeSupabaseClient())

    with pytest.raises(SupabaseVectorStoreError) as exc_info:
        store.upsert_chunks([_chunk(id="chunk-1")], [])

    assert str(exc_info.value) == "chunks and embeddings must have the same length."


def test_supabase_vector_store_upsert_maps_chunks_and_embeddings_to_rows() -> None:
    client = FakeSupabaseClient()
    store = SupabaseVectorStore(client=client)
    chunk = _chunk(id="chunk-1", source_url="https://drive.google.com/doc")

    store.upsert_chunks([chunk], [[0.1, 0.2]])

    assert client.upsert_calls == [
        {
            "table": "document_chunks",
            "rows": [
                {
                    "id": "chunk-1",
                    "folder_id": "folder-1",
                    "document_id": "document-1",
                    "drive_file_id": "drive-file-1",
                    "document_name": "Document",
                    "source_url": "https://drive.google.com/doc",
                    "chunk_index": 0,
                    "text": "chunk text",
                    "embedding": [0.1, 0.2],
                }
            ],
        }
    ]


def test_supabase_vector_store_search_maps_rpc_results_to_retrieved_chunks() -> None:
    client = FakeSupabaseClient(
        rpc_rows=[
            {
                "id": "chunk-1",
                "document_id": "document-1",
                "document_name": "Document",
                "source_url": "https://drive.google.com/doc",
                "chunk_index": 2,
                "text": "matched text",
                "score": 0.87,
            }
        ]
    )
    store = SupabaseVectorStore(client=client)

    results = store.search("folder-1", query_embedding=[0.1, 0.2], limit=3)

    assert client.rpc_calls == [
        {
            "function_name": "match_document_chunks",
            "params": {
                "query_embedding": [0.1, 0.2],
                "match_folder_id": "folder-1",
                "match_count": 3,
            },
        }
    ]
    assert len(results) == 1
    assert results[0].chunk_id == "chunk-1"
    assert results[0].document_id == "document-1"
    assert results[0].document_name == "Document"
    assert results[0].source_url == "https://drive.google.com/doc"
    assert results[0].chunk_index == 2
    assert results[0].text == "matched text"
    assert results[0].score == 0.87


def test_supabase_vector_store_delete_folder_filters_by_folder_id() -> None:
    client = FakeSupabaseClient()
    store = SupabaseVectorStore(client=client)

    store.delete_folder("folder-1")

    assert client.delete_calls == [{"table": "document_chunks"}]
    assert client.eq_calls == [{"column": "folder_id", "value": "folder-1"}]


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
