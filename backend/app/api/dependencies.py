from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.ai.answer_generator import AnswerGenerator
from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import VectorStore
from app.core.config import get_settings
from app.domain.chat.service import ChatService
from app.domain.folders.service import FolderIndexingService
from app.integrations.google.drive import GoogleDriveClient
from app.integrations.google.extraction import GoogleDriveExtractor
from app.integrations.google.oauth import get_tokens_from_session
from app.storage.chroma_store import ChromaVectorStore
from app.storage.supabase_vector_store import SupabaseVectorStore


def get_google_access_token(request: Request) -> str:
    tokens = get_tokens_from_session(request.session)
    if tokens is None:
        raise _unauthorized()

    return tokens.access_token


def get_vector_store() -> VectorStore:
    settings = get_settings()
    if settings.vector_store_provider == "supabase":
        return SupabaseVectorStore(settings=settings)

    return ChromaVectorStore(settings=settings)


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_answer_generator() -> AnswerGenerator:
    return AnswerGenerator()


def get_folder_indexing_service(
    access_token: Annotated[str, Depends(get_google_access_token)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> FolderIndexingService:
    return FolderIndexingService(
        drive_client=GoogleDriveClient(access_token),
        extractor=GoogleDriveExtractor(access_token),
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


def get_chat_service(
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
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
        detail="Connect Google Drive before indexing a folder.",
    )
