import pytest
from fastapi.testclient import TestClient

from app.ai.answer_generator import AnswerGenerationError
from app.ai.embeddings import EmbeddingError
from app.ai.models import Citation, RetrievedChunk
from app.api.dependencies import get_chat_service, get_folder_indexing_service
from app.api.schemas import ChatResponse
from app.domain.chat.service import InvalidChatMessageError
from app.domain.documents.models import SkippedFile
from app.domain.folders.models import IndexedFolder
from app.main import app
from app.storage.chroma_store import VectorStoreError
from app.storage.supabase_vector_store import SupabaseVectorStoreError


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


class FakeFolderIndexingService:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.folder_urls: list[str] = []

    def index_folder(self, folder_url: str) -> IndexedFolder:
        self.folder_urls.append(folder_url)
        if self.error is not None:
            raise self.error

        return IndexedFolder(
            folder_id="folder-123",
            folder_url=folder_url,
            name=None,
            files_found=2,
            files_indexed=1,
            chunks_created=3,
            skipped_files=[
                SkippedFile(
                    file_id="file-2",
                    name="image.png",
                    mime_type="image/png",
                    reason="Unsupported file type.",
                )
            ],
        )


class FakeChatService:
    def __init__(
        self,
        response: ChatResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls: list[dict[str, str]] = []

    def answer_question(self, folder_id: str, message: str) -> ChatResponse:
        self.calls.append({"folder_id": folder_id, "message": message})
        if self.error is not None:
            raise self.error

        if self.response is None:
            raise InvalidChatMessageError("Chat message is required.")

        return self.response


def test_auth_me_returns_unauthenticated_without_session(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"authenticated": False}


def test_index_folder_returns_401_without_session(client: TestClient) -> None:
    response = client.post(
        "/api/folders/index",
        json={"folder_url": "https://drive.google.com/drive/folders/folder-123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Connect Google Drive before indexing a folder."


def test_index_folder_cors_preflight_does_not_return_405(
    client: TestClient,
) -> None:
    response = client.options(
        "/api/folders/index",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_index_folder_returns_summary_when_authenticated(client: TestClient) -> None:
    service = FakeFolderIndexingService()
    app.dependency_overrides[get_folder_indexing_service] = lambda: service

    response = client.post(
        "/api/folders/index",
        json={"folder_url": "https://drive.google.com/drive/folders/folder-123"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "folder_id": "folder-123",
        "folder_url": "https://drive.google.com/drive/folders/folder-123",
        "files_found": 2,
        "files_indexed": 1,
        "chunks_created": 3,
        "skipped_files": [
            {
                "file_id": "file-2",
                "name": "image.png",
                "mime_type": "image/png",
                "reason": "Unsupported file type.",
            }
        ],
    }
    assert service.folder_urls == ["https://drive.google.com/drive/folders/folder-123"]


@pytest.mark.parametrize(
    "error",
    [
        VectorStoreError("Could not update local vector store."),
        SupabaseVectorStoreError("Could not delete document chunks."),
    ],
)
def test_index_folder_logs_vector_store_failures_and_returns_502(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
    error: Exception,
) -> None:
    app.dependency_overrides[get_folder_indexing_service] = lambda: (
        FakeFolderIndexingService(error=error)
    )

    response = client.post(
        "/api/folders/index",
        json={"folder_url": "https://drive.google.com/drive/folders/folder-123"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == str(error)
    assert "Folder indexing failed while updating the vector store." in caplog.text


def test_chat_returns_400_for_empty_message(client: TestClient) -> None:
    app.dependency_overrides[get_chat_service] = lambda: FakeChatService()

    response = client.post(
        "/api/chat",
        json={"folder_id": "folder-123", "message": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Chat message is required."


def test_chat_returns_answer_response(client: TestClient) -> None:
    chat_response = ChatResponse(
        answer="The plan is to index Drive files.",
        confidence="high",
        citations=[
            Citation(
                chunk_id="chunk-1",
                document_name="Plan",
                source_url="https://drive.google.com/doc-1",
                quote="index Drive files",
            )
        ],
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="chunk-1",
                document_id="doc-1",
                document_name="Plan",
                source_url="https://drive.google.com/doc-1",
                chunk_index=0,
                text="The plan is to index Drive files.",
                score=0.12,
            )
        ],
    )
    service = FakeChatService(response=chat_response)
    app.dependency_overrides[get_chat_service] = lambda: service

    response = client.post(
        "/api/chat",
        json={"folder_id": "folder-123", "message": "What is the plan?"},
    )

    assert response.status_code == 200
    assert response.json() == chat_response.model_dump()
    assert service.calls == [
        {"folder_id": "folder-123", "message": "What is the plan?"}
    ]


@pytest.mark.parametrize(
    "error",
    [
        EmbeddingError("Could not create embeddings."),
        VectorStoreError("Could not search vector store."),
        AnswerGenerationError("Could not generate a valid answer."),
    ],
)
def test_chat_logs_known_system_failures_and_returns_502(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
    error: Exception,
) -> None:
    app.dependency_overrides[get_chat_service] = lambda: FakeChatService(error=error)

    response = client.post(
        "/api/chat",
        json={"folder_id": "folder-123", "message": "What is the plan?"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == str(error)
    assert "Chat request failed during retrieval or answer generation." in caplog.text
