from app.ai.answer_generator import FALLBACK_ANSWER, AnswerGenerator
from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import VectorStore
from app.api.schemas import ChatResponse


class InvalidChatMessageError(ValueError):
    """Raised when a user chat message cannot be answered."""


class ChatService:
    """Coordinates retrieval and answer generation for one folder question."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        answer_generator: AnswerGenerator,
        retrieval_limit: int = 8,
    ) -> None:
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        self._answer_generator = answer_generator
        self._retrieval_limit = retrieval_limit

    def answer_question(self, folder_id: str, message: str) -> ChatResponse:
        """Answer a user question using only chunks retrieved from one folder."""

        cleaned_message = message.strip()
        if not cleaned_message:
            raise InvalidChatMessageError("Chat message is required.")

        query_embedding = self._embedding_service.embed_text(cleaned_message)
        retrieved_chunks = self._vector_store.search(
            folder_id=folder_id,
            query_embedding=query_embedding,
            limit=self._retrieval_limit,
        )

        if not retrieved_chunks:
            return ChatResponse(
                answer=FALLBACK_ANSWER,
                confidence="low",
                citations=[],
                retrieved_chunks=[],
            )

        answer = self._answer_generator.generate_answer(
            question=cleaned_message,
            chunks=retrieved_chunks,
        )
        return ChatResponse(
            answer=answer.answer,
            confidence=answer.confidence,
            citations=answer.citations,
            retrieved_chunks=retrieved_chunks,
        )
