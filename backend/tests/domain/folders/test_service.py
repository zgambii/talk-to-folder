from app.domain.documents.models import DriveFile, SourceDocument
from app.domain.folders.service import FolderIndexingService
from app.integrations.google.extraction import (
    DocumentExtractionError,
    UnsupportedFileTypeError,
)


# These fakes keep service tests focused on orchestration, not external APIs.
class FakeDriveClient:
    def __init__(
        self,
        files: list[DriveFile],
        *,
        folder_name: str | None = "Q4 Planning",
    ) -> None:
        self.files = files
        self._folder_name = folder_name
        self.listed_folder_ids: list[str] = []

    def get_file_name(self, file_id: str) -> str | None:
        del file_id
        return self._folder_name

    def list_folder_files(self, folder_id: str) -> list[DriveFile]:
        self.listed_folder_ids.append(folder_id)
        return self.files


class FakeExtractor:
    def __init__(self, results: dict[str, SourceDocument | Exception]) -> None:
        self.results = results
        self.extracted_file_ids: list[str] = []

    def extract_text(self, file: DriveFile) -> SourceDocument:
        self.extracted_file_ids.append(file.id)
        result = self.results[file.id]
        if isinstance(result, Exception):
            raise result

        return result


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.embedded_text_batches: list[list[str]] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.embedded_text_batches.append(texts)
        return [[float(index), 1.0] for index, _ in enumerate(texts)]


class FakeVectorStore:
    def __init__(self) -> None:
        self.deleted_folder_ids: list[str] = []
        self.upsert_calls: list[tuple[list[object], list[list[float]]]] = []

    def delete_folder(self, folder_id: str) -> None:
        self.deleted_folder_ids.append(folder_id)

    def upsert_chunks(
        self, chunks: list[object], embeddings: list[list[float]]
    ) -> None:
        self.upsert_calls.append((chunks, embeddings))

    def search(
        self,
        folder_id: str,
        query_embedding: list[float],
        limit: int = 8,
    ) -> list[object]:
        return []


def test_index_folder_successfully_indexes_supported_files() -> None:
    file = _drive_file(id="file-1", name="notes.txt")
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore()
    service = _service(
        files=[file],
        extraction_results={"file-1": _source_document(file, text="a" * 3500)},
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = service.index_folder("https://drive.google.com/drive/folders/folder-123")

    assert result.folder_id == "folder-123"
    assert result.name == "Q4 Planning"
    assert result.files_found == 1
    assert result.files_indexed == 1
    assert result.chunks_created == 2
    assert result.skipped_files == []
    assert vector_store.deleted_folder_ids == ["folder-123"]
    assert len(vector_store.upsert_calls) == 1

    upserted_chunks, embeddings = vector_store.upsert_calls[0]
    assert [chunk.id for chunk in upserted_chunks] == [
        "file-1:chunk:0",
        "file-1:chunk:1",
    ]
    assert embeddings == [[0.0, 1.0], [1.0, 1.0]]
    assert embedding_service.embedded_text_batches == [
        [chunk.text for chunk in upserted_chunks]
    ]


def test_index_folder_skips_unsupported_file_and_continues() -> None:
    unsupported_file = _drive_file(
        id="image-1", name="diagram.png", mime_type="image/png"
    )
    supported_file = _drive_file(id="text-1", name="notes.txt")
    service = _service(
        files=[unsupported_file, supported_file],
        extraction_results={
            "image-1": UnsupportedFileTypeError("File type is not supported."),
            "text-1": _source_document(supported_file, text="Indexed text"),
        },
    )

    result = service.index_folder("https://drive.google.com/drive/folders/folder-123")

    assert result.files_found == 2
    assert result.files_indexed == 1
    assert result.chunks_created == 1
    assert len(result.skipped_files) == 1
    assert result.skipped_files[0].file_id == "image-1"
    assert result.skipped_files[0].reason == "File type is not supported."


def test_index_folder_skips_extraction_failure_and_continues() -> None:
    failed_file = _drive_file(
        id="failed-1", name="broken.pdf", mime_type="application/pdf"
    )
    supported_file = _drive_file(id="text-1", name="notes.txt")
    service = _service(
        files=[failed_file, supported_file],
        extraction_results={
            "failed-1": DocumentExtractionError("Could not extract file text."),
            "text-1": _source_document(supported_file, text="Indexed text"),
        },
    )

    result = service.index_folder("https://drive.google.com/drive/folders/folder-123")

    assert result.files_indexed == 1
    assert result.chunks_created == 1
    assert len(result.skipped_files) == 1
    assert result.skipped_files[0].file_id == "failed-1"
    assert result.skipped_files[0].reason == "Could not extract file text."


def test_index_folder_skips_documents_that_produce_zero_chunks() -> None:
    file = _drive_file(id="empty-1", name="empty.txt")
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore()
    service = _service(
        files=[file],
        extraction_results={"empty-1": _source_document(file, text="  \n\n  ")},
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = service.index_folder("https://drive.google.com/drive/folders/folder-123")

    assert result.files_found == 1
    assert result.files_indexed == 0
    assert result.chunks_created == 0
    assert len(result.skipped_files) == 1
    assert result.skipped_files[0].reason == "No extractable text found."
    assert embedding_service.embedded_text_batches == []
    assert vector_store.upsert_calls == []


def test_index_folder_deletes_existing_vectors_before_upsert() -> None:
    file = _drive_file(id="file-1", name="notes.txt")
    vector_store = FakeVectorStore()
    service = _service(
        files=[file],
        extraction_results={"file-1": _source_document(file, text="Indexed text")},
        vector_store=vector_store,
    )

    service.index_folder("https://drive.google.com/drive/folders/folder-123")

    assert vector_store.deleted_folder_ids == ["folder-123"]
    assert vector_store.upsert_calls


def test_index_folder_with_no_supported_chunks_does_not_embed_or_upsert() -> None:
    file = _drive_file(id="image-1", name="diagram.png", mime_type="image/png")
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore()
    service = _service(
        files=[file],
        extraction_results={
            "image-1": UnsupportedFileTypeError("File type is not supported.")
        },
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = service.index_folder("https://drive.google.com/drive/folders/folder-123")

    assert result.files_found == 1
    assert result.files_indexed == 0
    assert result.chunks_created == 0
    assert embedding_service.embedded_text_batches == []
    assert vector_store.deleted_folder_ids == ["folder-123"]
    assert vector_store.upsert_calls == []


def _service(
    files: list[DriveFile],
    extraction_results: dict[str, SourceDocument | Exception],
    embedding_service: FakeEmbeddingService | None = None,
    vector_store: FakeVectorStore | None = None,
) -> FolderIndexingService:
    return FolderIndexingService(
        drive_client=FakeDriveClient(files),
        extractor=FakeExtractor(extraction_results),
        embedding_service=embedding_service or FakeEmbeddingService(),
        vector_store=vector_store or FakeVectorStore(),
    )


def _drive_file(
    id: str,
    name: str,
    mime_type: str = "text/plain",
) -> DriveFile:
    return DriveFile(id=id, name=name, mime_type=mime_type)


def _source_document(file: DriveFile, text: str) -> SourceDocument:
    return SourceDocument(
        id=file.id,
        drive_file_id=file.id,
        name=file.name,
        mime_type=file.mime_type,
        source_url=file.web_url,
        text=text,
    )
