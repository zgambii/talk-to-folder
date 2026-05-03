from app.ai.models import RetrievedChunk


def build_answer_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Build a source-grounded prompt from retrieved folder chunks."""

    chunk_blocks = "\n\n".join(_format_chunk(chunk) for chunk in chunks)
    return f"""You answer questions about an indexed Google Drive folder.

Use only the provided context. Do not invent facts.
If the context is insufficient, say that you do not know.
Every citation must reference one of the provided chunk_ids.
Citation quotes must be short and copied exactly from the provided chunk text.

Question:
{question}

Context:
{chunk_blocks}
"""


def _format_chunk(chunk: RetrievedChunk) -> str:
    return (
        f"chunk_id: {chunk.chunk_id}\n"
        f"document_name: {chunk.document_name}\n"
        f"chunk_index: {chunk.chunk_index}\n"
        f"text:\n{chunk.text}"
    )
