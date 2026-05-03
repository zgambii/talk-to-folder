from typing import Any

import pytest
from googleapiclient.errors import Error as GoogleApiError

from app.domain.documents.models import DriveFile
from app.integrations.google.drive import (
    GoogleDriveClient,
    GoogleDriveIntegrationError,
)


class FakeListRequest:
    def __init__(self, response: dict[str, Any] | Exception) -> None:
        self._response = response

    def execute(self) -> dict[str, Any]:
        if isinstance(self._response, Exception):
            raise self._response

        return self._response


class FakeFilesResource:
    def __init__(self, responses: list[dict[str, Any] | Exception]) -> None:
        self._responses = responses
        self.list_calls: list[dict[str, Any]] = []

    def list(self, **kwargs: Any) -> FakeListRequest:
        self.list_calls.append(kwargs)
        return FakeListRequest(self._responses.pop(0))


class FakeDriveService:
    def __init__(self, responses: list[dict[str, Any] | Exception]) -> None:
        self.files_resource = FakeFilesResource(responses)

    def files(self) -> FakeFilesResource:
        return self.files_resource


def test_list_folder_files_combines_pages_and_normalizes_files() -> None:
    service = FakeDriveService(
        [
            {
                "nextPageToken": "page-2",
                "files": [
                    {
                        "id": "file-1",
                        "name": "Notes",
                        "mimeType": "application/vnd.google-apps.document",
                        "webViewLink": "https://drive.google.com/file-1",
                        "createdTime": "2026-01-01T00:00:00Z",
                        "modifiedTime": "2026-01-02T00:00:00Z",
                    }
                ],
            },
            {
                "files": [
                    {
                        "id": "file-2",
                        "name": "Plan.pdf",
                        "mimeType": "application/pdf",
                    }
                ],
            },
        ]
    )
    client = _client_with_service(service)

    files = client.list_folder_files("folder-123")

    assert files == [
        DriveFile(
            id="file-1",
            name="Notes",
            mime_type="application/vnd.google-apps.document",
            web_url="https://drive.google.com/file-1",
            created_time="2026-01-01T00:00:00Z",
            modified_time="2026-01-02T00:00:00Z",
        ),
        DriveFile(id="file-2", name="Plan.pdf", mime_type="application/pdf"),
    ]
    assert service.files_resource.list_calls == [
        {
            "q": "'folder-123' in parents and trashed = false",
            "fields": (
                "nextPageToken,files("
                "id,name,mimeType,webViewLink,createdTime,modifiedTime"
                ")"
            ),
            "pageToken": None,
        },
        {
            "q": "'folder-123' in parents and trashed = false",
            "fields": (
                "nextPageToken,files("
                "id,name,mimeType,webViewLink,createdTime,modifiedTime"
                ")"
            ),
            "pageToken": "page-2",
        },
    ]


def test_list_folder_files_wraps_google_api_errors() -> None:
    service = FakeDriveService([GoogleApiError("api failed")])
    client = _client_with_service(service)

    with pytest.raises(GoogleDriveIntegrationError) as exc_info:
        client.list_folder_files("folder-123")

    assert str(exc_info.value) == "Could not list files from the Google Drive folder."
    assert isinstance(exc_info.value.__cause__, GoogleApiError)


def _client_with_service(service: FakeDriveService) -> GoogleDriveClient:
    client = GoogleDriveClient.__new__(GoogleDriveClient)
    client._service = service
    return client
