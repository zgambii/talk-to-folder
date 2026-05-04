from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.folders import router as folders_router
from app.core.config import get_settings

app = FastAPI(title="Talk to Folder API")

settings = get_settings()
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if settings.frontend_origin is not None:
    allowed_origins.append(settings.frontend_origin)
if settings.frontend_url not in allowed_origins:
    allowed_origins.append(settings.frontend_url)

session_cookie_secure = settings.environment == "production"
session_same_site = "none" if session_cookie_secure else "lax"

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    session_cookie=settings.session_cookie_name,
    same_site=session_same_site,
    https_only=session_cookie_secure,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(folders_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
