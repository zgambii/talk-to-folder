from app.ai.models import RetrievedChunk


def build_answer_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Build a source-grounded prompt from retrieved folder chunks."""

    chunk_blocks = "\n\n".join(_format_chunk(chunk) for chunk in chunks)
    return f"""You answer questions about an indexed Google Drive folder.

Use only the provided context. Do not invent facts.
Return only a valid JSON object. Do not wrap the JSON in markdown.
Do not include extra commentary before or after the JSON.
If the context is insufficient, return a low-confidence JSON answer with an
empty citations array.
Every citation.chunk_id must exactly match one of the provided chunk_id values.
Citation quotes must be short and copied exactly from the provided chunk text.

The JSON object must match this shape:
{{
  "answer": "string",
  "confidence": "low | medium | high",
  "citations": [
    {{
      "chunk_id": "string",
      "document_name": "string",
      "source_url": "string or null",
      "quote": "short exact quote from the retrieved chunk"
    }}
  ]
}}

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
