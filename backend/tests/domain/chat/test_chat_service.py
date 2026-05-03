import pytest

from app.ai.answer_generator import FALLBACK_ANSWER
from app.ai.models import Citation, FolderAnswer, RetrievedChunk
from app.domain.chat.service import ChatService, InvalidChatMessageError


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.embedded_texts: list[str] = []

    def embed_text(self, text: str) -> list[float]:
        self.embedded_texts.append(text)
        return [1.0, 0.0]


class FakeVectorStore:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self.chunks = chunks
        self.search_calls: list[dict[str, object]] = []

    def search(
        self,
        folder_id: str,
        query_embedding: list[float],
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        self.search_calls.append(
            {
                "folder_id": folder_id,
                "query_embedding": query_embedding,
                "limit": limit,
            }
        )
        return self.chunks


class FakeAnswerGenerator:
    def __init__(self, answer: FolderAnswer) -> None:
        self.answer = answer
        self.calls: list[dict[str, object]] = []

    def generate_answer(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> FolderAnswer:
        self.calls.append({"question": question, "chunks": chunks})
        return self.answer


def test_answer_question_embeds_retrieves_and_generates_answer() -> None:
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore(chunks=[_chunk()])
    answer_generator = FakeAnswerGenerator(answer=_answer())
    service = ChatService(
        embedding_service=embedding_service,
        vector_store=vector_store,
        answer_generator=answer_generator,
        retrieval_limit=3,
    )

    response = service.answer_question("folder-1", "  What is the plan?  ")

    assert embedding_service.embedded_texts == ["What is the plan?"]
    assert vector_store.search_calls == [
        {
            "folder_id": "folder-1",
            "query_embedding": [1.0, 0.0],
            "limit": 3,
        }
    ]
    assert answer_generator.calls == [
        {"question": "What is the plan?", "chunks": [_chunk()]}
    ]
    assert response.answer == "The plan is to index Drive files."


def test_answer_question_rejects_empty_message() -> None:
    service = ChatService(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(chunks=[]),
        answer_generator=FakeAnswerGenerator(answer=_answer()),
    )

    with pytest.raises(InvalidChatMessageError):
        service.answer_question("folder-1", "   ")


def test_answer_question_returns_fallback_when_no_chunks_are_retrieved() -> None:
    answer_generator = FakeAnswerGenerator(answer=_answer())
    service = ChatService(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(chunks=[]),
        answer_generator=answer_generator,
    )

    response = service.answer_question("folder-1", "What is the plan?")

    assert response.answer == FALLBACK_ANSWER
    assert response.confidence == "low"
    assert response.citations == []
    assert response.retrieved_chunks == []
    assert answer_generator.calls == []


def test_answer_question_includes_retrieved_chunks_in_response() -> None:
    chunk = _chunk()
    service = ChatService(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(chunks=[chunk]),
        answer_generator=FakeAnswerGenerator(answer=_answer()),
    )

    response = service.answer_question("folder-1", "What is the plan?")

    assert response.retrieved_chunks == [chunk]


def test_answer_question_maps_answer_generator_output() -> None:
    citation = Citation(
        chunk_id="chunk-1",
        document_name="Plan",
        source_url="https://drive.google.com/doc-1",
        quote="index Drive files",
    )
    answer = FolderAnswer(
        answer="The plan is to index Drive files.",
        confidence="high",
        citations=[citation],
    )
    service = ChatService(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(chunks=[_chunk()]),
        answer_generator=FakeAnswerGenerator(answer=answer),
    )

    response = service.answer_question("folder-1", "What is the plan?")

    assert response.answer == answer.answer
    assert response.confidence == answer.confidence
    assert response.citations == [citation]


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        document_name="Plan",
        source_url="https://drive.google.com/doc-1",
        chunk_index=0,
        text="The plan is to index Drive files.",
        score=0.1,
    )


def _answer() -> FolderAnswer:
    return FolderAnswer(
        answer="The plan is to index Drive files.",
        confidence="medium",
        citations=[
            Citation(
                chunk_id="chunk-1",
                document_name="Plan",
                source_url="https://drive.google.com/doc-1",
                quote="index Drive files",
            )
        ],
    )
