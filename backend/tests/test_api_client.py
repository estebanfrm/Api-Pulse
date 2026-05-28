from typing import Any

import httpx
import pytest

from app.services import api_client


def test_execute_api_request_returns_parsed_response_summary_and_safe_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_request: dict[str, Any] = {}

    class SuccessfulClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.timeout = kwargs["timeout"]
            self.follow_redirects = kwargs["follow_redirects"]

        def __enter__(self) -> "SuccessfulClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def request(self, **kwargs: object) -> httpx.Response:
            captured_request.update(kwargs)
            return httpx.Response(
                200,
                json={"ok": True},
                headers={
                    "content-type": "application/json",
                    "content-length": "12",
                    "server": "test-server",
                    "x-secret": "hidden",
                },
                request=httpx.Request(str(kwargs["method"]), str(kwargs["url"])),
            )

    monkeypatch.setattr(api_client.httpx, "Client", SuccessfulClient)

    result = api_client.execute_api_request(
        url="https://api.example.com",
        method="POST",
        headers={"X-Test": "1"},
        body={"name": "pulse"},
    )

    assert result.success is True
    assert result.status_code == 200
    assert result.response_body == {"ok": True}
    assert result.response_summary == '{"ok": true}'
    assert result.error_message is None
    assert result.response_headers == {
        "content-type": "application/json",
        "content-length": "12",
        "server": "test-server",
    }
    assert captured_request["json"] == {"name": "pulse"}


@pytest.mark.parametrize(
    ("exception", "expected_message"),
    [
        (httpx.ConnectTimeout("connect took too long"), "Connection timeout."),
        (httpx.ReadTimeout("read took too long"), "Read timeout."),
        (httpx.ConnectError("name resolution failed"), "Connection error."),
    ],
)
def test_execute_api_request_classifies_http_client_errors(
    monkeypatch: pytest.MonkeyPatch,
    exception: httpx.HTTPError,
    expected_message: str,
) -> None:
    class FailingClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

