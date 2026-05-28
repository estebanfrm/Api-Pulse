import pytest
from fastapi.testclient import TestClient


BASE_PAYLOAD = {"method": "GET", "headers": {}, "body": {}}


def _payload(url: str, **overrides: object) -> dict[str, object]:
    data = {"url": url, **BASE_PAYLOAD}
    data.update(overrides)
    return data


def test_url_without_scheme_is_saved_as_format_error(client: TestClient) -> None:
    response = client.post("/api/checks", json=_payload("api.github.com"))

    assert response.status_code == 200
    check = response.json()["check"]
    assert check["success"] is False
    assert check["status_code"] is None
    assert check["error_message"].startswith("Invalid URL format.")


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://0.0.0.0",
        "http://[::1]",
        "http://10.0.0.5",
        "http://169.254.10.20",
        "http://224.0.0.1",
        "http://240.0.0.1",
        "http://[::]",
    ],
)
def test_blocked_targets_are_saved_as_failures(client: TestClient, url: str) -> None:
    response = client.post("/api/checks", json=_payload(url))

    assert response.status_code == 200
    check = response.json()["check"]
    assert check["url"] == url
    assert check["success"] is False
    assert check["status_code"] is None
    assert check["error_message"].startswith("Blocked target.")

    history = client.get("/api/checks?limit=5").json()
    assert history[0]["url"] == url
    assert history[0]["success"] is False


def test_rejects_invalid_header_values(client: TestClient) -> None:
    response = client.post(
        "/api/checks",
        json=_payload("https://api.example.com", headers={"X-Nested": {"value": "not allowed"}}),
    )

    assert response.status_code == 422


def test_rejects_invalid_body_payload(client: TestClient) -> None:
    response = client.post(
        "/api/checks",
        json=_payload("https://api.example.com", body=["not", "an", "object"]),
    )

    assert response.status_code == 422


def test_rejects_invalid_method(client: TestClient) -> None:
    response = client.post("/api/checks", json=_payload("https://api.example.com", method="PATCH"))

    assert response.status_code == 422
