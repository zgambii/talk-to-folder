from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.folders import router as folders_router

app = FastAPI(title="Talk to Folder API")
app.include_router(folders_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
