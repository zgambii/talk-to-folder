from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.ai.answer_generator import AnswerGenerator
from app.ai.embeddings import EmbeddingService
from app.domain.chat.service import ChatService
from app.domain.folders.service import FolderIndexingService
from app.integrations.google.drive import GoogleDriveClient
from app.integrations.google.extraction import GoogleDriveExtractor
from app.storage.chroma_store import ChromaVectorStore


def get_bearer_token(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if authorization is None:
        raise _unauthorized()

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise _unauthorized()

    return token.strip()


def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore()


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_answer_generator() -> AnswerGenerator:
    return AnswerGenerator()


def get_folder_indexing_service(
    access_token: Annotated[str, Depends(get_bearer_token)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    vector_store: Annotated[ChromaVectorStore, Depends(get_vector_store)],
) -> FolderIndexingService:
    return FolderIndexingService(
        drive_client=GoogleDriveClient(access_token),
        extractor=GoogleDriveExtractor(access_token),
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


def get_chat_service(
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    vector_store: Annotated[ChromaVectorStore, Depends(get_vector_store)],
    answer_generator: Annotated[AnswerGenerator, Depends(get_answer_generator)],
) -> ChatService:
    return ChatService(
        embedding_service=embedding_service,
        vector_store=vector_store,
        answer_generator=answer_generator,
    )


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authorization header must be in the form 'Bearer <access_token>'.",
    )
