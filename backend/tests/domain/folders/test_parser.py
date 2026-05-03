import pytest

from app.domain.folders.parser import (
    InvalidDriveFolderUrlError,
    parse_google_drive_folder_url,
)


@pytest.mark.parametrize(
    ("folder_url", "expected_folder_id"),
    [
        ("https://drive.google.com/drive/folders/folder-123", "folder-123"),
        ("https://drive.google.com/drive/u/0/folders/folder-123", "folder-123"),
        ("https://drive.google.com/drive/u/1/folders/folder-123", "folder-123"),
        ("https://drive.google.com/open?id=folder-123", "folder-123"),
        (
            "https://drive.google.com/drive/folders/folder-123?usp=sharing",
            "folder-123",
        ),
        ("drive.google.com/drive/folders/folder-123", "folder-123"),
        ("  https://drive.google.com/drive/folders/folder-123  ", "folder-123"),
    ],
)
def test_parse_google_drive_folder_url_returns_folder_id(
    folder_url: str,
    expected_folder_id: str,
) -> None:
    assert parse_google_drive_folder_url(folder_url) == expected_folder_id


@pytest.mark.parametrize(
    "folder_url",
    [
        "",
        "   ",
        "https://example.com/drive/folders/folder-123",
        "https://drive.google.com/file/d/file-123/view",
        "https://drive.google.com/random/folders/abc123",
        "https://drive.google.com/drive/folders/",
        "https://drive.google.com/open",
        "https://drive.google.com/open?id=",
    ],
)
def test_parse_google_drive_folder_url_rejects_invalid_urls(
    folder_url: str,
) -> None:
    with pytest.raises(InvalidDriveFolderUrlError):
        parse_google_drive_folder_url(folder_url)
