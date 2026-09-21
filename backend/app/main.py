from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings, settings
from app.database import SessionLocal, engine, init_database
from app.routers.checks import _prune_history, router as checks_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_database()
    if settings.public_demo:
        with SessionLocal() as db:
            _prune_history(db)
    yield


# redirect_slashes stays off: uvicorn runs with --no-proxy-headers, so Starlette would
# build the slash redirect from the unencrypted origin scheme and answer an HTTPS
# request with an http:// Location. The checks routes accept both spellings instead.
app = FastAPI(title="API Pulse", version="0.1.0", redirect_slashes=False, lifespan=lifespan)

CHECKS_PATH = "/api/checks"


class DemoBodyLimitMiddleware:
    def __init__(self, wrapped_app: object) -> None:
        self.wrapped_app = wrapped_app

    async def __call__(self, scope: dict, receive: object, send: object) -> None:
        if not (settings.public_demo and scope["type"] == "http" and scope["method"] == "POST"):
            await self.wrapped_app(scope, receive, send)
            return
        if (scope["path"].rstrip("/") or "/") != CHECKS_PATH:
            await self.wrapped_app(scope, receive, send)
            return

        max_bytes = settings.demo_max_request_bytes
        for name, value in scope["headers"]:
            if name.lower() == b"content-length" and value.isdigit() and int(value) > max_bytes:
                await JSONResponse({"detail": "Demo request exceeded the size limit."}, status_code=413)(scope, receive, send)
                return

        chunks = []
        length = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            length += len(chunk)
            if length > max_bytes:
                await JSONResponse({"detail": "Demo request exceeded the size limit."}, status_code=413)(scope, receive, send)
                return
            chunks.append(chunk)
            if not message.get("more_body", False):
                break

        delivered = False

        async def replay() -> dict:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()

        await self.wrapped_app(scope, replay, send)


app.add_middleware(DemoBodyLimitMiddleware)


def cors_options(config: Settings) -> dict[str, object]:
    public = config.app_env == "production"
    return {
        "allow_origins": [config.frontend_origin],
        "allow_origin_regex": None if public else r"http://(localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}):5173",
        "allow_credentials": not public,
        "allow_methods": ["GET", "POST"] if public else ["*"],
        "allow_headers": ["Content-Type"] if public else ["*"],
    }


app.add_middleware(CORSMiddleware, **cors_options(settings))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable.") from None
    return {"status": "ready"}


app.include_router(checks_router, prefix=CHECKS_PATH, tags=["checks"])
