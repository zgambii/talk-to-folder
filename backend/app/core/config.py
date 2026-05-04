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
    openai_answer_model: str
    chroma_path: str
    frontend_origin: str | None
    app_env: str
    google_client_id: str | None
    google_client_secret: str | None
    google_redirect_uri: str
    frontend_url: str
    session_secret_key: str


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings for dependency-free config access."""

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_embedding_model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        ),
        openai_answer_model=os.getenv("OPENAI_ANSWER_MODEL", "gpt-4.1-mini"),
        chroma_path=os.getenv("CHROMA_PATH", ".chroma"),
        frontend_origin=os.getenv("FRONTEND_ORIGIN"),
        app_env=os.getenv("APP_ENV", "development"),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        google_redirect_uri=os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/auth/google/callback",
        ),
        frontend_url=os.getenv("FRONTEND_URL", "http://localhost:5173"),
        session_secret_key=os.getenv("SESSION_SECRET_KEY", "dev-session-secret"),
    )
