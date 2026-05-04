from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from app.core.config import get_settings
from app.integrations.google.oauth import (
    SESSION_STATE_KEY,
    GoogleOAuthError,
    build_google_authorization_url,
    clear_oauth_session,
    create_oauth_state,
    exchange_authorization_code,
    get_tokens_from_session,
    store_tokens_in_session,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthStatusResponse(BaseModel):
    authenticated: bool


class LogoutResponse(BaseModel):
    success: bool


@router.get("/google/login")
def google_login(request: Request) -> RedirectResponse:
    settings = get_settings()
    state = create_oauth_state()
    request.session[SESSION_STATE_KEY] = state

    try:
        authorization_url = build_google_authorization_url(settings, state)
    except GoogleOAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return RedirectResponse(authorization_url)


@router.get("/google/callback")
def google_callback(
    request: Request, code: str | None = None, state: str | None = None
):
    expected_state = request.session.get(SESSION_STATE_KEY)
    if not code or not state or state != expected_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google OAuth callback.",
        )

    try:
        tokens = exchange_authorization_code(code, get_settings())
    except GoogleOAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    store_tokens_in_session(_session(request), tokens)
    request.session.pop(SESSION_STATE_KEY, None)
    return RedirectResponse(get_settings().frontend_url)


@router.get("/me", response_model=AuthStatusResponse)
def auth_status(request: Request) -> AuthStatusResponse:
    return AuthStatusResponse(
        authenticated=get_tokens_from_session(_session(request)) is not None
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(request: Request) -> LogoutResponse:
    clear_oauth_session(_session(request))
    return LogoutResponse(success=True)


def _session(request: Request) -> dict[str, Any]:
    return request.session
