from typing import Any

import httpx
import pytest

from app.services import api_client


def test_execute_api_request_returns_parsed_response_summary_and_safe_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_client_options: dict[str, Any] = {}
    captured_request: dict[str, Any] = {}

    class SuccessfulClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured_client_options.update(kwargs)

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
    assert captured_client_options["follow_redirects"] is False
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

        def __enter__(self) -> "FailingClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def request(self, **kwargs: object) -> httpx.Response:
            raise exception

    monkeypatch.setattr(api_client.httpx, "Client", FailingClient)

    result = api_client.execute_api_request(
        url="https://api.example.com",
        method="GET",
        headers={},
        body=None,
    )

    assert result.success is False
    assert result.status_code is None
    assert result.response_time_ms is not None
    assert result.response_time_ms >= 0
    assert result.response_summary == ""
    assert result.response_body is None
    assert result.response_headers == {}
    assert result.error_message is not None
    assert result.error_message.startswith(expected_message)


@pytest.mark.parametrize("status_code", [404, 500])
def test_execute_api_request_treats_http_error_status_as_received_response(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
) -> None:
    class ResponseClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def __enter__(self) -> "ResponseClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def request(self, **kwargs: object) -> httpx.Response:
            return httpx.Response(
                status_code,
                json={"received": True},
                request=httpx.Request(str(kwargs["method"]), str(kwargs["url"])),
            )

    monkeypatch.setattr(api_client.httpx, "Client", ResponseClient)

    result = api_client.execute_api_request(
        url="https://api.example.com",
        method="GET",
        headers={},
        body=None,
    )

    assert result.success is True
    assert result.status_code == status_code
    assert result.response_body == {"received": True}
    assert result.error_message is None


def test_execute_api_request_does_not_send_body_for_get(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_request: dict[str, Any] = {}

    class GetClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def __enter__(self) -> "GetClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def request(self, **kwargs: object) -> httpx.Response:
            captured_request.update(kwargs)
            return httpx.Response(
                200,
                text="ok",
                request=httpx.Request(str(kwargs["method"]), str(kwargs["url"])),
            )

    monkeypatch.setattr(api_client.httpx, "Client", GetClient)

    api_client.execute_api_request(
        url="https://api.example.com",
        method="GET",
        headers={},
        body={"must_not_be_sent": True},
    )

    assert captured_request["method"] == "GET"
    assert captured_request["json"] is None


def test_execute_api_request_truncates_response_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    response_text = "abcdefghijklmno"

    class TextResponseClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def __enter__(self) -> "TextResponseClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def request(self, **kwargs: object) -> httpx.Response:
            return httpx.Response(
                200,
                text=response_text,
                request=httpx.Request(str(kwargs["method"]), str(kwargs["url"])),
            )

    monkeypatch.setattr(api_client.httpx, "Client", TextResponseClient)
    monkeypatch.setattr(api_client.settings, "response_summary_max_chars", 10)

    result = api_client.execute_api_request(
        url="https://api.example.com",
        method="GET",
        headers={},
        body=None,
    )

    assert result.response_body == response_text
    assert result.response_summary == response_text[:10]
    assert len(result.response_summary) == 10
