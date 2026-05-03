from pydantic import BaseModel

from app.domain.documents.models import SkippedFile


# Folder models describe Google Drive folder references and indexing results.
class FolderRef(BaseModel):
    folder_id: str
    folder_url: str
    name: str | None = None


class IndexedFolder(BaseModel):
    folder_id: str
    folder_url: str
    name: str | None = None
    files_found: int
    files_indexed: int
    chunks_created: int
    skipped_files: list[SkippedFile]
