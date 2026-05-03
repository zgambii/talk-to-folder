import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables.

    Keeping these values in one small object prevents provider details and local
    storage paths from being hardcoded throughout the app.
    """

    openai_api_key: str | None
    openai_embedding_model: str
    chroma_path: str


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings for dependency-free config access."""

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_embedding_model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        ),
        chroma_path=os.getenv("CHROMA_PATH", ".chroma"),
    )
