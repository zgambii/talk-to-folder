import pytest

from app.domain.documents.chunking import (
    InvalidChunkingConfigError,
    chunk_document,
)
from app.domain.documents.models import SourceDocument


def test_chunk_document_returns_one_chunk_for_short_document() -> None:
    document = _source_document(text="A short document.")

    chunks = chunk_document(document, folder_id="folder-1")

    assert len(chunks) == 1
    assert chunks[0].text == "A short document."


def test_chunk_document_returns_multiple_chunks_for_long_document() -> None:
    document = _source_document(text="a" * 25)

    chunks = chunk_document(
        document, folder_id="folder-1", chunk_size=10, chunk_overlap=2
    )

    assert [chunk.text for chunk in chunks] == ["a" * 10, "a" * 10, "a" * 9]


def test_chunk_document_applies_overlap() -> None:
    document = _source_document(text="abcdefghijklmnopqrstuvwxyz")

    chunks = chunk_document(
        document, folder_id="folder-1", chunk_size=10, chunk_overlap=3
    )

    assert chunks[0].text[-3:] == chunks[1].text[:3]
    assert chunks[1].text == "hijklmnopq"


def test_chunk_document_returns_empty_list_for_blank_document() -> None:
    document = _source_document(text=" \n\n\t ")

    assert chunk_document(document, folder_id="folder-1") == []


def test_chunk_document_uses_deterministic_chunk_ids() -> None:
    document = _source_document(id="document-123", text="a" * 25)

    chunks = chunk_document(
        document, folder_id="folder-1", chunk_size=10, chunk_overlap=0
    )

    assert [chunk.id for chunk in chunks] == [
        "document-123:chunk:0",
        "document-123:chunk:1",
        "document-123:chunk:2",
    ]


def test_chunk_document_preserves_metadata() -> None:
    document = _source_document(
        id="document-123",
        drive_file_id="drive-file-123",
        name="Design notes",
        source_url="https://drive.google.com/file",
        text="Document text",
    )

    chunk = chunk_document(document, folder_id="folder-123")[0]

    assert chunk.folder_id == "folder-123"
    assert chunk.document_id == "document-123"
    assert chunk.drive_file_id == "drive-file-123"
    assert chunk.document_name == "Design notes"
    assert chunk.source_url == "https://drive.google.com/file"
    assert chunk.chunk_index == 0


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [
        (0, 0),
        (-1, 0),
        (10, -1),
        (10, 10),
    ],
)
def test_chunk_document_rejects_invalid_config(
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    document = _source_document(text="Document text")

    with pytest.raises(InvalidChunkingConfigError):
        chunk_document(
            document,
            folder_id="folder-1",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )


def test_chunk_document_prefers_paragraph_boundaries_when_reasonable() -> None:
    first_paragraph = "A" * 20
    second_paragraph = "B" * 20
    third_paragraph = "C" * 20
    document = _source_document(
        text=f"{first_paragraph}\n\n{second_paragraph}\n\n{third_paragraph}"
    )

    chunks = chunk_document(
        document, folder_id="folder-1", chunk_size=45, chunk_overlap=0
    )

    assert chunks[0].text == f"{first_paragraph}\n\n{second_paragraph}"
    assert chunks[1].text == third_paragraph


def test_chunk_document_chunks_very_long_paragraph() -> None:
    document = _source_document(text="x" * 35)

    chunks = chunk_document(
        document, folder_id="folder-1", chunk_size=10, chunk_overlap=0
    )

    assert [len(chunk.text) for chunk in chunks] == [10, 10, 10, 5]


def test_chunk_document_normalizes_line_endings_and_excess_blank_lines() -> None:
    document = _source_document(text="First\r\n\r\n\r\nSecond\rThird")

    chunks = chunk_document(document, folder_id="folder-1")

    assert chunks[0].text == "First\n\nSecond\nThird"


def _source_document(
    text: str,
    id: str = "document-1",
    drive_file_id: str = "drive-file-1",
    name: str = "Document",
    mime_type: str = "text/plain",
    source_url: str | None = None,
) -> SourceDocument:
    return SourceDocument(
        id=id,
        drive_file_id=drive_file_id,
        name=name,
        mime_type=mime_type,
        source_url=source_url,
        text=text,
    )
