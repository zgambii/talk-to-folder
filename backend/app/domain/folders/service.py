from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import VectorStore
from app.domain.documents.chunking import chunk_document
from app.domain.documents.models import DocumentChunk, DriveFile, SkippedFile
from app.domain.folders.models import IndexedFolder
from app.domain.folders.parser import parse_google_drive_folder_url
from app.integrations.google.drive import GoogleDriveClient
from app.integrations.google.extraction import (
    DocumentExtractionError,
    GoogleDriveExtractor,
    UnsupportedFileTypeError,
)


class FolderIndexingService:
    """Coordinates folder indexing across Drive, extraction, embeddings, and storage."""

    def __init__(
        self,
        drive_client: GoogleDriveClient,
        extractor: GoogleDriveExtractor,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self._drive_client = drive_client
        self._extractor = extractor
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    def index_folder(self, folder_url: str) -> IndexedFolder:
        """Index a Drive folder into the vector store and return a run summary.

        Per-file extraction problems are reported as skipped files so one bad
        document does not block the rest of the folder. Embedding and vector
        store errors are intentionally allowed to fail the run because they mean
        the index would be incomplete or inconsistent.
        """

        folder_id = parse_google_drive_folder_url(folder_url)
        folder_name = self._drive_client.get_file_name(folder_id)
        files = self._drive_client.list_folder_files(folder_id)

        # Re-indexing replaces the folder's previous vectors with a fresh set.
        self._vector_store.delete_folder(folder_id)

        skipped_files: list[SkippedFile] = []
        chunks: list[DocumentChunk] = []
        files_indexed = 0

        for file in files:
            file_chunks = self._extract_file_chunks(file, folder_id, skipped_files)
            if not file_chunks:
                continue

            chunks.extend(file_chunks)
            files_indexed += 1

        if chunks:
            # Embedding in one batch keeps provider calls predictable and lets
            # the vector store receive chunks and embeddings in matching order.
            embeddings = self._embedding_service.embed_texts(
                [chunk.text for chunk in chunks]
            )
            self._vector_store.upsert_chunks(chunks, embeddings)

        return IndexedFolder(
            folder_id=folder_id,
            folder_url=folder_url.strip(),
            name=folder_name,
            files_found=len(files),
            files_indexed=files_indexed,
            chunks_created=len(chunks),
            skipped_files=skipped_files,
        )

    def _extract_file_chunks(
        self,
        file: DriveFile,
        folder_id: str,
        skipped_files: list[SkippedFile],
    ) -> list[DocumentChunk]:
        """Extract and chunk one file, adding recoverable failures to skipped_files."""

        try:
            document = self._extractor.extract_text(file)
        except UnsupportedFileTypeError as exc:
            skipped_files.append(
                _skipped_file(file, _reason(exc, "Unsupported file type."))
            )
            return []
        except DocumentExtractionError as exc:
            skipped_files.append(
                _skipped_file(file, _reason(exc, "Could not extract file text."))
            )
            return []

        chunks = chunk_document(document, folder_id)
        if not chunks:
            skipped_files.append(_skipped_file(file, "No extractable text found."))

        return chunks


def _skipped_file(file: DriveFile, reason: str) -> SkippedFile:
    return SkippedFile(
        file_id=file.id,
        name=file.name,
        mime_type=file.mime_type,
        reason=reason,
    )


def _reason(exc: Exception, fallback: str) -> str:
    return str(exc) or fallback
