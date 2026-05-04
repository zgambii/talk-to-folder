from pathlib import Path

from pytest import MonkeyPatch

from app.core import config


def test_get_settings_loads_backend_env_file(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "GOOGLE_CLIENT_ID=test-client-id",
                "GOOGLE_CLIENT_SECRET=test-client-secret",
                "GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback",
                "FRONTEND_URL=http://localhost:5173",
                "SESSION_SECRET_KEY=test-session-secret",
                "VECTOR_STORE_PROVIDER=supabase",
                "SUPABASE_URL=https://example.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=test-service-role-key",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(config, "ENV_FILE_PATH", env_file)
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("GOOGLE_REDIRECT_URI", raising=False)
    monkeypatch.delenv("FRONTEND_URL", raising=False)
    monkeypatch.delenv("SESSION_SECRET_KEY", raising=False)
    monkeypatch.delenv("VECTOR_STORE_PROVIDER", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    config.get_settings.cache_clear()

    settings = config.get_settings()

    assert settings.google_client_id == "test-client-id"
    assert settings.google_client_secret == "test-client-secret"
    assert (
        settings.google_redirect_uri == "http://localhost:8000/api/auth/google/callback"
    )
    assert settings.frontend_url == "http://localhost:5173"
    assert settings.session_secret_key == "test-session-secret"
    assert settings.vector_store_provider == "supabase"
    assert settings.supabase_url == "https://example.supabase.co"
    assert settings.supabase_service_role_key == "test-service-role-key"

    config.get_settings.cache_clear()
