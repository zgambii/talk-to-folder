from app.domain.documents.models import DocumentChunk, SourceDocument


class InvalidChunkingConfigError(ValueError):
    """Raised when document chunking settings cannot produce valid chunks."""


def chunk_document(
    document: SourceDocument,
    folder_id: str,
    chunk_size: int = 3000,
    chunk_overlap: int = 300,
) -> list[DocumentChunk]:
    _validate_chunking_config(chunk_size, chunk_overlap)

    text = _normalize_text(document.text)
    if not text:
        return []

    chunks: list[DocumentChunk] = []
    start_index = 0

    while start_index < len(text):
        end_index = _find_chunk_end(text, start_index, chunk_size)
        chunk_text = text[start_index:end_index].strip()

        if chunk_text:
            chunks.append(
                _build_chunk(
                    document=document,
                    folder_id=folder_id,
                    chunk_index=len(chunks),
                    text=chunk_text,
                )
            )

        if end_index >= len(text):
            break

        next_start = end_index - chunk_overlap
        start_index = max(next_start, start_index + 1)

    return chunks


def _validate_chunking_config(chunk_size: int, chunk_overlap: int) -> None:
    if chunk_size <= 0:
        raise InvalidChunkingConfigError("chunk_size must be greater than 0.")

    if chunk_overlap < 0:
        raise InvalidChunkingConfigError(
            "chunk_overlap must be greater than or equal to 0."
        )

    if chunk_overlap >= chunk_size:
        raise InvalidChunkingConfigError(
            "chunk_overlap must be smaller than chunk_size."
        )


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n")]

    output_lines: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = not line
        if is_blank and previous_blank:
            continue

        output_lines.append(line)
        previous_blank = is_blank

    return "\n".join(output_lines).strip()


def _find_chunk_end(text: str, start_index: int, chunk_size: int) -> int:
    max_end = min(start_index + chunk_size, len(text))
    if max_end == len(text):
        return max_end

    paragraph_boundary = text.rfind("\n\n", start_index, max_end)
    minimum_useful_boundary = start_index + max(1, chunk_size // 2)
    if paragraph_boundary >= minimum_useful_boundary:
        return paragraph_boundary

    return max_end


def _build_chunk(
    document: SourceDocument,
    folder_id: str,
    chunk_index: int,
    text: str,
) -> DocumentChunk:
    return DocumentChunk(
        id=f"{document.id}:chunk:{chunk_index}",
        folder_id=folder_id,
        document_id=document.id,
        drive_file_id=document.drive_file_id,
        document_name=document.name,
        source_url=document.source_url,
        chunk_index=chunk_index,
        text=text,
    )
