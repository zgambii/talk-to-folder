from collections.abc import Mapping
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import Error as GoogleApiError

from app.domain.documents.models import DriveFile


class GoogleDriveIntegrationError(RuntimeError):
    """Raised when Google Drive cannot complete a requested operation."""


class GoogleDriveClient:
    def __init__(self, access_token: str) -> None:
        credentials = Credentials(token=access_token)
        self._service = build("drive", "v3", credentials=credentials)

    def list_folder_files(self, folder_id: str) -> list[DriveFile]:
        files: list[DriveFile] = []
        page_token: str | None = None

        try:
            while True:
                response = (
                    self._service.files()
                    .list(
                        q=f"'{folder_id}' in parents and trashed = false",
                        fields=(
                            "nextPageToken,files("
                            "id,name,mimeType,webViewLink,createdTime,modifiedTime"
                            ")"
                        ),
                        pageToken=page_token,
                    )
                    .execute()
                )

                raw_files = response.get("files", [])
                files.extend(_normalize_drive_file(raw_file) for raw_file in raw_files)

                page_token = response.get("nextPageToken")
                if not page_token:
                    return files
        except GoogleApiError as exc:
            raise GoogleDriveIntegrationError(
                "Could not list files from the Google Drive folder."
            ) from exc


def _normalize_drive_file(raw_file: Mapping[str, Any]) -> DriveFile:
    return DriveFile(
        id=str(raw_file["id"]),
        name=str(raw_file["name"]),
        mime_type=str(raw_file["mimeType"]),
        web_url=raw_file.get("webViewLink"),
        created_time=raw_file.get("createdTime"),
        modified_time=raw_file.get("modifiedTime"),
    )
