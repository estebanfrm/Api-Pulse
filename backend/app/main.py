from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_database
from app.routers.checks import router as checks_router

app = FastAPI(title="API Pulse", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(checks_router, prefix="/api/checks", tags=["checks"])
