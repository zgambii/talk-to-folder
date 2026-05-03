from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(folders_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
