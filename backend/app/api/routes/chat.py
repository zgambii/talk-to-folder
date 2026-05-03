from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.answer_generator import AnswerGenerationError
from app.ai.embeddings import EmbeddingError
from app.api.dependencies import get_chat_service
from app.api.schemas import ChatRequest, ChatResponse
from app.domain.chat.service import ChatService, InvalidChatMessageError

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def answer_chat_question(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatResponse:
    try:
        return service.answer_question(
            folder_id=request.folder_id,
            message=request.message,
        )
    except InvalidChatMessageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (AnswerGenerationError, EmbeddingError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
