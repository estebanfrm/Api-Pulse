import os
from typing import Literal
from urllib.parse import urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    app_env: Literal["development", "production"] = "development"
    database_url: str = "postgresql+psycopg://api_pulse:api_pulse_password@postgres:5432/api_pulse"
    frontend_origin: str = "http://localhost:5173"
    request_timeout_seconds: float = 20.0
    response_summary_max_chars: int = 2000
    public_demo: bool = True
    demo_requests_per_minute_ip: int = 10
    demo_requests_per_minute_global: int = 60
    demo_concurrent_ip: int = 2
    demo_concurrent_global: int = 10
    demo_max_request_bytes: int = 16 * 1024
    demo_max_response_bytes: int = 64 * 1024
    demo_timeout_seconds: float = 8.0
    history_retention_hours: int = 24
    history_max_records: int = 500

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


def validate_production_settings(config: Settings) -> None:
    if os.getenv("RENDER") == "true" and config.app_env != "production":
        raise RuntimeError("Render requires APP_ENV=production.")
    if config.app_env != "production":
        return
    if not config.public_demo:
        raise RuntimeError("Production requires the controlled public demo mode.")
    try:
        origin = urlsplit(config.frontend_origin)
        valid_origin = (
            origin.scheme == "https"
            and bool(origin.hostname)
            and origin.netloc == origin.hostname
            and not origin.path
            and not origin.query
            and not origin.fragment
        )
    except ValueError:
        valid_origin = False
    if not valid_origin:
        raise RuntimeError("Production FRONTEND_ORIGIN must be one HTTPS origin.")
    try:
        database = make_url(config.database_url)
        host = (database.host or "").lower()
        valid_database = (
            database.drivername == "postgresql+psycopg"
            and host.endswith(".neon.tech")
            and "-pooler." in host
            and database.query.get("sslmode") in {"require", "verify-full"}
            and database.query.get("channel_binding") == "require"
        )
    except (ArgumentError, TypeError, ValueError):
        valid_database = False
    if not valid_database:
        raise RuntimeError("Production DATABASE_URL must be a pooled Neon psycopg URL with TLS and channel binding.")


validate_production_settings(settings)
