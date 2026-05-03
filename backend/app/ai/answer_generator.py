from typing import Any, Protocol

from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from app.ai.models import FolderAnswer, RetrievedChunk
from app.ai.prompts import build_answer_prompt
from app.core.config import Settings, get_settings

FALLBACK_ANSWER = (
    "I could not find enough information in the indexed folder to answer that."
)


class AnswerGenerationError(Exception):
    """Raised when the answer provider returns unusable output."""


class _ResponsesResource(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class _AnswerClient(Protocol):
    responses: _ResponsesResource


class AnswerGenerator:
    """Generates source-grounded answers from retrieved chunks."""

    def __init__(
        self,
        model_name: str | None = None,
        client: _AnswerClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._model_name = model_name or self._settings.openai_answer_model
        self._client = client or OpenAI(api_key=self._settings.openai_api_key)

    def generate_answer(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> FolderAnswer:
        if not chunks:
            return FolderAnswer(answer=FALLBACK_ANSWER, confidence="low", citations=[])

        prompt = build_answer_prompt(question, chunks)
        try:
            response = self._client.responses.create(
                model=self._model_name,
                input=prompt,
                text={"format": {"type": "json_object"}},
            )
            answer = FolderAnswer.model_validate_json(response.output_text)
        except (OpenAIError, ValidationError, ValueError) as exc:
            raise AnswerGenerationError("Could not generate a valid answer.") from exc

        _validate_citations(answer, chunks)
        return answer


def _validate_citations(answer: FolderAnswer, chunks: list[RetrievedChunk]) -> None:
    known_chunk_ids = {chunk.chunk_id for chunk in chunks}
    for citation in answer.citations:
        if citation.chunk_id not in known_chunk_ids:
            raise AnswerGenerationError(
                f"Answer cited an unknown chunk_id: {citation.chunk_id}"
            )

        if not citation.quote.strip():
            raise AnswerGenerationError("Answer included an empty citation quote.")
