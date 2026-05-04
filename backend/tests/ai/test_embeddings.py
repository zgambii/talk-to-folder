from dataclasses import dataclass

import pytest
from openai import APIConnectionError

from app.ai.embeddings import EmbeddingError, EmbeddingService
from app.core.config import Settings


@dataclass
class FakeEmbedding:
    embedding: list[float]


@dataclass
class FakeEmbeddingResponse:
    data: list[FakeEmbedding]


class FakeEmbeddingsResource:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, model: str, input: list[str]) -> FakeEmbeddingResponse:
        self.calls.append({"model": model, "input": input})
        return FakeEmbeddingResponse(
            data=[
                FakeEmbedding([float(index), float(len(text))])
                for index, text in enumerate(input)
            ]
        )


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.embeddings = FakeEmbeddingsResource()


class FailingEmbeddingsResource:
    def create(self, model: str, input: list[str]) -> FakeEmbeddingResponse:
        raise APIConnectionError(request=None)


class FailingOpenAIClient:
    def __init__(self) -> None:
        self.embeddings = FailingEmbeddingsResource()


def test_embed_text_returns_single_embedding() -> None:
    client = FakeOpenAIClient()
    service = EmbeddingService(
        client=client,
        settings=_settings(model="test-embedding-model"),
    )

    embedding = service.embed_text("hello")

    assert embedding == [0.0, 5.0]
    assert client.embeddings.calls == [
        {"model": "test-embedding-model", "input": ["hello"]}
    ]


def test_embed_texts_returns_embeddings_in_order() -> None:
    service = EmbeddingService(
        client=FakeOpenAIClient(),
        settings=_settings(model="test-embedding-model"),
    )

    embeddings = service.embed_texts(["alpha", "beta"])

    assert embeddings == [[0.0, 5.0], [1.0, 4.0]]


def test_embed_texts_wraps_provider_errors() -> None:
    service = EmbeddingService(
        client=FailingOpenAIClient(),
        settings=_settings(model="test-embedding-model"),
    )

    with pytest.raises(EmbeddingError) as exc_info:
        service.embed_texts(["hello"])

    assert str(exc_info.value) == "Could not create embeddings."
    assert isinstance(exc_info.value.__cause__, APIConnectionError)


def _settings(model: str) -> Settings:
    return Settings(
        openai_api_key="test-key",
        openai_embedding_model=model,
        openai_answer_model="test-answer-model",
        chroma_path=".chroma-test",
        vector_store_provider="chroma",
        supabase_url=None,
        supabase_service_role_key=None,
        frontend_origin="http://localhost:5173",
        app_env="test",
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        google_redirect_uri="http://localhost:8000/api/auth/google/callback",
        frontend_url="http://localhost:5173",
        session_secret_key="test-session-secret",
    )
