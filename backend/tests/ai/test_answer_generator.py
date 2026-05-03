from dataclasses import dataclass

import pytest

from app.ai.answer_generator import (
    FALLBACK_ANSWER,
    AnswerGenerationError,
    AnswerGenerator,
)
from app.ai.models import FolderAnswer, RetrievedChunk
from app.ai.prompts import build_answer_prompt
from app.core.config import Settings


@dataclass
class FakeResponse:
    output_text: str


class FakeResponsesResource:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> FakeResponse:
        self.calls.append(kwargs)
        return FakeResponse(output_text=self.output_text)


class FakeOpenAIClient:
    def __init__(self, output_text: str) -> None:
        self.responses = FakeResponsesResource(output_text)


def test_generate_answer_returns_low_confidence_fallback_for_empty_chunks() -> None:
    client = FakeOpenAIClient(_valid_answer_json())
    generator = AnswerGenerator(client=client, settings=_settings())

    answer = generator.generate_answer("What is the plan?", [])

    assert answer == FolderAnswer(
        answer=FALLBACK_ANSWER, confidence="low", citations=[]
    )
    assert client.responses.calls == []


def test_generate_answer_returns_valid_structured_output() -> None:
    client = FakeOpenAIClient(_valid_answer_json())
    generator = AnswerGenerator(client=client, settings=_settings())

    answer = generator.generate_answer("What is the plan?", [_chunk()])

    assert answer.answer == "The plan is to index Drive files."
    assert answer.confidence == "high"
    assert answer.citations[0].chunk_id == "chunk-1"
    assert client.responses.calls[0]["model"] == "test-answer-model"
    assert client.responses.calls[0]["text"] == {"format": {"type": "json_object"}}


def test_generate_answer_wraps_invalid_json() -> None:
    generator = AnswerGenerator(
        client=FakeOpenAIClient("not-json"), settings=_settings()
    )

    with pytest.raises(AnswerGenerationError):
        generator.generate_answer("What is the plan?", [_chunk()])


def test_generate_answer_rejects_unknown_citation_chunk_id() -> None:
    generator = AnswerGenerator(
        client=FakeOpenAIClient("""
            {
              "answer": "The plan is to index Drive files.",
              "confidence": "medium",
              "citations": [
                {
                  "chunk_id": "missing",
                  "document_name": "Plan",
                  "source_url": null,
                  "quote": "index Drive files"
                }
              ]
            }
            """),
        settings=_settings(),
    )

    with pytest.raises(AnswerGenerationError) as exc_info:
        generator.generate_answer("What is the plan?", [_chunk()])

    assert str(exc_info.value) == "Answer cited an unknown chunk_id: missing"


def test_generate_answer_rejects_empty_citation_quote() -> None:
    generator = AnswerGenerator(
        client=FakeOpenAIClient("""
            {
              "answer": "The plan is to index Drive files.",
              "confidence": "medium",
              "citations": [
                {
                  "chunk_id": "chunk-1",
                  "document_name": "Plan",
                  "source_url": null,
                  "quote": " "
                }
              ]
            }
            """),
        settings=_settings(),
    )

    with pytest.raises(AnswerGenerationError) as exc_info:
        generator.generate_answer("What is the plan?", [_chunk()])

    assert str(exc_info.value) == "Answer included an empty citation quote."


def test_build_answer_prompt_includes_question_and_chunk_details() -> None:
    prompt = build_answer_prompt("What is the plan?", [_chunk()])

    assert "What is the plan?" in prompt
    assert "chunk_id: chunk-1" in prompt
    assert "document_name: Plan" in prompt
    assert "chunk_index: 2" in prompt
    assert "Only" not in prompt
    assert "Use only the provided context." in prompt


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        document_name="Plan",
        source_url="https://drive.google.com/doc-1",
        chunk_index=2,
        text="The plan is to index Drive files.",
        score=0.12,
    )


def _valid_answer_json() -> str:
    return """
    {
      "answer": "The plan is to index Drive files.",
      "confidence": "high",
      "citations": [
        {
          "chunk_id": "chunk-1",
          "document_name": "Plan",
          "source_url": "https://drive.google.com/doc-1",
          "quote": "index Drive files"
        }
      ]
    }
    """


def _settings() -> Settings:
    return Settings(
        openai_api_key="test-key",
        openai_embedding_model="test-embedding-model",
        openai_answer_model="test-answer-model",
        chroma_path=".chroma-test",
    )
