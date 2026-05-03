import pytest
from fastapi.testclient import TestClient

from app.ai.models import Citation, RetrievedChunk
from app.api.dependencies import get_chat_service, get_folder_indexing_service
from app.api.schemas import ChatResponse
from app.domain.chat.service import InvalidChatMessageError
from app.domain.documents.models import SkippedFile
from app.domain.folders.models import IndexedFolder
from app.main import app


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


class FakeFolderIndexingService:
    def __init__(self) -> None:
        self.folder_urls: list[str] = []

    def index_folder(self, folder_url: str) -> IndexedFolder:
        self.folder_urls.append(folder_url)
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
    def __init__(self, response: ChatResponse | None = None) -> None:
        self.response = response
        self.calls: list[dict[str, str]] = []

    def answer_question(self, folder_id: str, message: str) -> ChatResponse:
        self.calls.append({"folder_id": folder_id, "message": message})
        if self.response is None:
            raise InvalidChatMessageError("Chat message is required.")

        return self.response


def test_index_folder_returns_401_without_authorization(client: TestClient) -> None:
    response = client.post(
        "/api/folders/index",
        json={"folder_url": "https://drive.google.com/drive/folders/folder-123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authorization header must be in the form 'Bearer <access_token>'."
    )


def test_index_folder_returns_summary_when_authorized(client: TestClient) -> None:
    service = FakeFolderIndexingService()
    app.dependency_overrides[get_folder_indexing_service] = lambda: service

    response = client.post(
        "/api/folders/index",
        headers={"Authorization": "Bearer test-token"},
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
