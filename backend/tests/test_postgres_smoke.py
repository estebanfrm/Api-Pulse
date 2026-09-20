"""CI-only public-demo smoke against an ephemeral PostgreSQL service."""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.skipif(os.getenv("TEST_POSTGRES_SMOKE") != "1", reason="Requires a dedicated ephemeral PostgreSQL database")
def test_public_check_survives_app_restart_with_postgres() -> None:
    payload = {"url": "https://demo.api-pulse.invalid/echo", "method": "POST", "body": {"example": True}}

    with TestClient(app) as first_client:
        assert first_client.get("/health").json() == {"status": "ok"}
        assert first_client.get("/ready").json() == {"status": "ready"}
        created = first_client.post("/api/checks", json=payload)
        assert created.status_code == 200
        assert created.json()["check"]["status_code"] == 201
        check_id = created.json()["check"]["id"]

    with TestClient(app) as restarted_client:
        assert restarted_client.get("/ready").status_code == 200
        history = restarted_client.get("/api/checks").json()
        assert any(check["id"] == check_id for check in history)
        assert "example" not in str(history)
