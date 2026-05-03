from collections.abc import Sequence
from typing import Protocol

from openai import OpenAI, OpenAIError

from app.core.config import Settings, get_settings


class EmbeddingError(RuntimeError):
    """Raised when an embedding provider cannot complete a request."""


class _EmbeddingClient(Protocol):
    """Small protocol for injecting a fake OpenAI client in tests."""

    embeddings: object


class EmbeddingService:
    """Creates vector embeddings for text through the configured OpenAI model."""

    def __init__(
        self,
        client: _EmbeddingClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        """Initialize the service with real settings or test doubles."""

        self._settings = settings or get_settings()
        self._client = client or OpenAI(api_key=self._settings.openai_api_key)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string and return its vector."""

        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple strings in one provider call and preserve input order."""

        try:
            response = self._client.embeddings.create(
                model=self._settings.openai_embedding_model,
                input=texts,
            )
        except OpenAIError as exc:
            raise EmbeddingError("Could not create embeddings.") from exc

        return [_coerce_embedding(item.embedding) for item in response.data]


def _coerce_embedding(embedding: Sequence[float]) -> list[float]:
    """Normalize provider vector values into plain Python floats."""

    return [float(value) for value in embedding]
