import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.config import Settings, validate_production_settings
from app import main


NEON_URL = (
    "postgresql+psycopg://demo:test-only@ep-example-pooler.us-east-1.aws.neon.tech/neondb"
    "?sslmode=require&channel_binding=require"
)


def production_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "app_env": "production",
        "public_demo": True,
        "frontend_origin": "https://api-pulse-web.onrender.com",
        "database_url": NEON_URL,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_production_accepts_controlled_demo_https_origin_and_pooled_neon() -> None:
    config = production_settings()

    validate_production_settings(config)
    assert main.cors_options(config) == {
        "allow_origins": ["https://api-pulse-web.onrender.com"],
        "allow_origin_regex": None,
        "allow_credentials": False,
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"],
    }


@pytest.mark.parametrize(
    "overrides",
    [
        {"public_demo": False},
        {"frontend_origin": "http://localhost:5173"},
        {"frontend_origin": "https://api-pulse-web.onrender.com/extra"},
        {"database_url": NEON_URL.replace("-pooler", "")},
        {"database_url": NEON_URL.replace("channel_binding=require", "channel_binding=disable")},
        {"database_url": "not-a-database-url"},
    ],
)
def test_production_rejects_unsafe_configuration_without_exposing_secret(overrides: dict[str, object]) -> None:
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_settings(production_settings(**overrides))

    assert "test-only" not in str(exc_info.value)


def test_development_preserves_local_cors_policy() -> None:
    config = Settings(_env_file=None, app_env="development")

    assert main.cors_options(config)["allow_origin_regex"] is not None
    assert main.cors_options(config)["allow_credentials"] is True


def test_render_does_not_allow_development_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RENDER", "true")

    with pytest.raises(RuntimeError, match="Render requires APP_ENV=production"):
        validate_production_settings(Settings(_env_file=None, app_env="development"))


def test_ready_checks_database_without_leaking_error(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    sqlite_engine = create_engine("sqlite+pysqlite://")
    monkeypatch.setattr(main, "engine", sqlite_engine)
    try:
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}
    finally:
        sqlite_engine.dispose()

    class FailingEngine:
        def connect(self) -> None:
            raise OperationalError("SELECT 1", {}, Exception("secret-internal-host"))

    monkeypatch.setattr(main, "engine", FailingEngine())
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable."}
    assert "secret-internal-host" not in response.text


def test_demo_concurrency_never_exceeds_the_connection_pool() -> None:
    # A surplus request would wait pool_timeout seconds and then fail with a 500
    # instead of being rejected with an honest 429.
    from app.config import settings
    from app.database import DB_POOL_CAPACITY

    assert settings.demo_concurrent_global <= DB_POOL_CAPACITY
    assert settings.demo_concurrent_ip <= settings.demo_concurrent_global
