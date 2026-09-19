from collections.abc import Generator
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

from app.config import settings
from app.database import get_db
from app.models import ApiCheck
from app.routers import checks
from app.services.limits import DemoLimiter


@pytest.fixture()
def demo_client(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(settings, "public_demo", True)
    monkeypatch.setattr(checks, "demo_limiter", DemoLimiter())
    return client


def _post(demo_client: TestClient, url: str, method: str = "GET", body: dict | None = None):
    return demo_client.post(
        "/api/checks",
        json={"url": url, "method": method, "headers": {}, "body": body or {}},
    )


@pytest.mark.parametrize("method,status", [("GET", 200), ("POST", 201), ("PUT", 200), ("DELETE", 200)])
def test_controlled_echo_supports_four_methods_without_real_network(
    demo_client: TestClient, monkeypatch: pytest.MonkeyPatch, method: str, status: int
) -> None:
    def no_dns(*args: object, **kwargs: object) -> None:
        raise AssertionError("Public demo must not resolve a network hostname")

    monkeypatch.setattr("socket.getaddrinfo", no_dns)
    response = _post(demo_client, "https://demo.api-pulse.invalid/echo", method, {"example": True})

    assert response.status_code == 200
    data = response.json()
    assert data["check"]["status_code"] == status
    assert data["check"]["success"] is True
    assert data["response"] == {"method": method, "body": None if method == "GET" else {"example": True}}
    assert data["check"]["response_summary"] == f"Demo {method} /echo: HTTP {status}"


@pytest.mark.parametrize("path,status", [("/status/404", 404), ("/status/500", 500), ("/redirect", 302)])
def test_controlled_error_and_redirect_are_received(demo_client: TestClient, path: str, status: int) -> None:
    response = _post(demo_client, f"https://demo.api-pulse.invalid{path}")

    assert response.status_code == 200
    assert response.json()["check"]["status_code"] == status
    assert response.json()["check"]["success"] is True


def test_public_request_uses_controlled_transport_and_demo_timeout(
    demo_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = checks.execute_api_request
    captured: dict[str, object] = {}

    def execute_with_capture(**kwargs):
        captured.update(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(checks, "execute_api_request", execute_with_capture)
    response = _post(demo_client, "https://demo.api-pulse.invalid/echo")

    assert response.status_code == 200
    assert captured["timeout_seconds"] == settings.demo_timeout_seconds == 8.0
    assert captured["transport"] is not None


@pytest.mark.parametrize(
    "url",
    [
        "https://api.example.com/resource?token=secret-value",
        "https://demo.api-pulse.invalid/echo?token=secret-value",
        "https://user:secret-value@demo.api-pulse.invalid/echo",
        "http://localhost:8000/private?token=secret-value",
        "https://[invalid/echo?token=secret-value",
    ],
)
def test_unlisted_target_is_rejected_without_persisting_user_url(demo_client: TestClient, url: str) -> None:
    response = _post(demo_client, url)

    assert response.status_code == 200
    check = response.json()["check"]
    assert check["success"] is False
    assert check["error_message"] == "Blocked target. Choose one of the demo scenarios."
    assert check["url"] == "https://demo.api-pulse.invalid/blocked"
    assert "secret-value" not in str(response.json())
    assert "secret-value" not in str(demo_client.get("/api/checks").json())


def test_public_history_never_exposes_request_body_or_headers(demo_client: TestClient) -> None:
    response = demo_client.post(
        "/api/checks",
        json={
            "url": "https://demo.api-pulse.invalid/echo",
            "method": "POST",
            "headers": {"Authorization": "Bearer header-secret"},
            "body": {"token": "body-secret"},
        },
    )

    assert response.status_code == 200
    assert response.json()["response"]["body"] == {"token": "body-secret"}
    history = demo_client.get("/api/checks").json()
    assert len(history) == 1
    assert "header-secret" not in str(history)
    assert "body-secret" not in str(history)


def test_request_body_is_bounded_before_schema_parsing(demo_client: TestClient) -> None:
    response = demo_client.post(
        "/api/checks",
        content=b"x" * (settings.demo_max_request_bytes + 1),
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert demo_client.get("/api/checks").json() == []


def test_response_size_limit_prevents_returning_oversized_body(
    demo_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "demo_max_response_bytes", 1)
    response = _post(demo_client, "https://demo.api-pulse.invalid/echo")

    assert response.status_code == 200
    assert response.json()["check"]["success"] is False
    assert response.json()["response"] is None
    assert response.json()["check"]["error_message"] == "Demo response exceeded the size limit."


def test_per_client_rate_limit_returns_429_without_history_entry(
    demo_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "demo_requests_per_minute_ip", 1)
    first = _post(demo_client, "https://demo.api-pulse.invalid/echo")
    second = _post(demo_client, "https://demo.api-pulse.invalid/echo")

    assert first.status_code == 200
    assert second.status_code == 429
    assert len(demo_client.get("/api/checks").json()) == 1


def test_concurrency_limit_rejects_second_request(demo_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "demo_concurrent_ip", 1)
    with checks.demo_limiter.admit("testclient"):
        response = _post(demo_client, "https://demo.api-pulse.invalid/echo")

    assert response.status_code == 429
    assert demo_client.get("/api/checks").json() == []


def test_history_prunes_by_count_and_age(demo_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "history_max_records", 3)
    for _ in range(4):
        assert _post(demo_client, "https://demo.api-pulse.invalid/echo").status_code == 200

    history = demo_client.get("/api/checks?limit=100").json()
    assert len(history) == 3

    override = demo_client.app.dependency_overrides[get_db]
    session_generator: Generator[Session, None, None] = override()
    db = next(session_generator)
    try:
        oldest = db.query(ApiCheck).order_by(ApiCheck.id).first()
        assert oldest is not None
        oldest_id = oldest.id
        oldest.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
        db.commit()
    finally:
        session_generator.close()

    remaining = demo_client.get("/api/checks?limit=100").json()
    assert len(remaining) == 2
    assert all(item["id"] != oldest_id for item in remaining)


def test_public_history_removes_legacy_records_before_listing(demo_client: TestClient) -> None:
    override = demo_client.app.dependency_overrides[get_db]
    session_generator: Generator[Session, None, None] = override()
    db = next(session_generator)
    try:
        db.add(ApiCheck(
            url="https://legacy.example.com/?token=old-secret",
            method="GET",
            response_summary="old-secret",
            success=True,
        ))
        db.commit()
    finally:
        session_generator.close()

    response = demo_client.get("/api/checks")

    assert response.status_code == 200
    assert response.json() == []
    assert "old-secret" not in response.text


def test_spoofed_forwarded_header_does_not_bypass_rate_limit(
    demo_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "demo_requests_per_minute_ip", 1)
    payload = {"url": "https://demo.api-pulse.invalid/echo", "method": "GET"}
    first = demo_client.post("/api/checks", json=payload, headers={"x-forwarded-for": "1.2.3.4"})
    second = demo_client.post("/api/checks", json=payload, headers={"x-forwarded-for": "5.6.7.8"})

    assert first.status_code == 200
    assert second.status_code == 429


def test_global_limit_applies_across_client_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    limiter = DemoLimiter()
    monkeypatch.setattr(settings, "demo_requests_per_minute_global", 1)

    with limiter.admit("first-client"):
        pass

    with pytest.raises(HTTPException) as exc_info:
        with limiter.admit("second-client"):
            pass

    assert exc_info.value.status_code == 429
    assert list(limiter._by_client) == ["first-client"]
    assert "second-client" not in limiter._active_by_client
