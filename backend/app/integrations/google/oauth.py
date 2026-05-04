import secrets
import time
from typing import Any
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from app.core.config import Settings

GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_DRIVE_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
SESSION_TOKEN_KEY = "google_oauth_tokens"
SESSION_STATE_KEY = "google_oauth_state"


class GoogleOAuthError(RuntimeError):
    """Raised when Google OAuth cannot complete successfully."""


class GoogleOAuthTokens(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_at: int | None = None
    token_type: str | None = None
    scope: str | None = None


class GoogleUserInfo(BaseModel):
    email: str | None = None
    name: str | None = None


def create_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def build_google_authorization_url(settings: Settings, state: str) -> str:
    _ensure_oauth_settings(settings)
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_DRIVE_READONLY_SCOPE,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"{GOOGLE_AUTHORIZATION_URL}?{query}"


def exchange_authorization_code(code: str, settings: Settings) -> GoogleOAuthTokens:
    _ensure_oauth_settings(settings)
    try:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GoogleOAuthError("Could not complete Google sign-in.") from exc

    return _tokens_from_response(response.json())


def fetch_google_user_info(access_token: str) -> GoogleUserInfo:
    try:
        response = httpx.get(
            GOOGLE_USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GoogleOAuthError("Could not fetch Google user info.") from exc

    data = response.json()
    return GoogleUserInfo(email=data.get("email"), name=data.get("name"))


def store_tokens_in_session(session: dict[str, Any], tokens: GoogleOAuthTokens) -> None:
    session[SESSION_TOKEN_KEY] = tokens.model_dump()


def get_tokens_from_session(session: dict[str, Any]) -> GoogleOAuthTokens | None:
    raw_tokens = session.get(SESSION_TOKEN_KEY)
    if not isinstance(raw_tokens, dict):
        return None

    return GoogleOAuthTokens.model_validate(raw_tokens)


def clear_oauth_session(session: dict[str, Any]) -> None:
    session.pop(SESSION_TOKEN_KEY, None)
    session.pop(SESSION_STATE_KEY, None)


def _tokens_from_response(data: dict[str, Any]) -> GoogleOAuthTokens:
    expires_in = data.get("expires_in")
    expires_at = int(time.time()) + int(expires_in) if expires_in is not None else None
    return GoogleOAuthTokens(
        access_token=str(data["access_token"]),
        refresh_token=data.get("refresh_token"),
        expires_at=expires_at,
        token_type=data.get("token_type"),
        scope=data.get("scope"),
    )


def _ensure_oauth_settings(settings: Settings) -> None:
    if not settings.google_client_id or not settings.google_client_secret:
        raise GoogleOAuthError("Google OAuth is not configured.")
