import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.embeddings import EmbeddingError
from app.api.dependencies import get_folder_indexing_service
from app.api.schemas import IndexFolderRequest, IndexFolderResponse
from app.domain.folders.parser import InvalidDriveFolderUrlError
from app.domain.folders.service import FolderIndexingService
from app.integrations.google.drive import GoogleDriveIntegrationError
from app.storage.chroma_store import VectorStoreError
from app.storage.supabase_vector_store import SupabaseVectorStoreError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/folders", tags=["folders"])


@router.post("/index", response_model=IndexFolderResponse)
def index_folder(
    request: IndexFolderRequest,
    service: Annotated[FolderIndexingService, Depends(get_folder_indexing_service)],
) -> IndexFolderResponse:
    try:
        indexed_folder = service.index_folder(request.folder_url)
    except InvalidDriveFolderUrlError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except GoogleDriveIntegrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except EmbeddingError as exc:
        logger.exception("Folder indexing failed during embedding.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except (VectorStoreError, SupabaseVectorStoreError) as exc:
        logger.exception("Folder indexing failed while updating the vector store.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return IndexFolderResponse.model_validate(indexed_folder.model_dump())
