from urllib.parse import parse_qs, urlparse

import httpx

from app.core.config import Settings
from app.integrations.google import oauth


def test_build_google_authorization_url_contains_drive_scope_and_state() -> None:
    url = oauth.build_google_authorization_url(_settings(), state="state-123")
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)

    assert parsed_url.netloc == "accounts.google.com"
    assert query["client_id"] == ["test-client-id"]
    assert query["redirect_uri"] == ["http://localhost:8000/api/auth/google/callback"]
    assert query["scope"] == [oauth.GOOGLE_DRIVE_READONLY_SCOPE]
    assert query["state"] == ["state-123"]
    assert query["access_type"] == ["offline"]


def test_exchange_authorization_code_returns_tokens(
    monkeypatch,
) -> None:
    def fake_post(url, data, timeout):
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "expires_in": 3600,
                "token_type": "Bearer",
                "scope": oauth.GOOGLE_DRIVE_READONLY_SCOPE,
            },
        )

    monkeypatch.setattr(oauth.httpx, "post", fake_post)

    tokens = oauth.exchange_authorization_code("code-123", _settings())

    assert tokens.access_token == "access-token"
    assert tokens.refresh_token == "refresh-token"
    assert tokens.expires_at is not None


def _settings() -> Settings:
    return Settings(
        openai_api_key="test-key",
        openai_embedding_model="test-embedding-model",
        openai_answer_model="test-answer-model",
        chroma_path=".chroma-test",
        frontend_origin="http://localhost:5173",
        app_env="test",
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        google_redirect_uri="http://localhost:8000/api/auth/google/callback",
        frontend_url="http://localhost:5173",
        session_secret_key="test-session-secret",
    )
