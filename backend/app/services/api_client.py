from dataclasses import dataclass
import json
from time import perf_counter
from typing import Any

import httpx

from app.config import settings


@dataclass(frozen=True)
class ApiClientResult:
    success: bool
    status_code: int | None
    response_time_ms: int | None
    response_summary: str
    response_body: Any | None
    response_headers: dict[str, str]
    error_message: str | None


def execute_api_request(
    *,
    url: str,
    method: str,
    headers: dict[str, str] | None,
    body: dict[str, Any] | None,
    transport: httpx.BaseTransport | None = None,
    timeout_seconds: float | None = None,
) -> ApiClientResult:
    start = perf_counter()
    effective_timeout = timeout_seconds if timeout_seconds is not None else settings.request_timeout_seconds
    try:
        with httpx.Client(
            timeout=effective_timeout,
            follow_redirects=False,
            **({"transport": transport} if transport is not None else {}),
        ) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method in {"POST", "PUT", "DELETE"} else None,
            )
        elapsed_ms = _elapsed_ms(start)
        response_body = _parse_response_body(response)
        summary = _summarize_response(response_body)
        return ApiClientResult(
            success=True,
            status_code=response.status_code,
            response_time_ms=elapsed_ms,
            response_summary=summary,
            response_body=response_body,
            response_headers=_safe_response_headers(response),
            error_message=None,
        )
    except httpx.ConnectTimeout:
        return _failure(start, f"Connection timeout. The server did not accept a connection within {effective_timeout:g} seconds.")
    except httpx.ReadTimeout:
        return _failure(start, f"Read timeout. The server did not send a response within {effective_timeout:g} seconds.")
    except httpx.TimeoutException:
        return _failure(start, f"Timeout. The request did not complete within {effective_timeout:g} seconds.")
    except httpx.ConnectError:
        return _failure(start, "Connection error. The host could not be reached.")
    except httpx.UnsupportedProtocol:
        return _failure(start, "Invalid URL format. Only http and https requests are supported.")
    except httpx.InvalidURL:
        return _failure(start, "Invalid URL format. The URL could not be parsed by the HTTP client.")
    except httpx.RemoteProtocolError:
        return _failure(start, "Protocol error. The server returned an invalid HTTP response.")
    except httpx.TransportError:
        return _failure(start, "Network error. The request could not be completed.")
    except httpx.HTTPError:
        return _failure(start, "HTTP client error.")
    except Exception:
        return _failure(start, "Unexpected request error.")


def _failure(start: float, message: str) -> ApiClientResult:
    return ApiClientResult(
        success=False,
        status_code=None,
        response_time_ms=_elapsed_ms(start),
        response_summary="",
        response_body=None,
        response_headers={},
        error_message=message,
    )


def _elapsed_ms(start: float) -> int:
    return max(0, round((perf_counter() - start) * 1000))


def _parse_response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def _summarize_response(response_body: Any) -> str:
    if isinstance(response_body, str):
        raw_summary = response_body
    else:
        raw_summary = json.dumps(response_body, ensure_ascii=False)
    return raw_summary[: settings.response_summary_max_chars]


def _safe_response_headers(response: httpx.Response) -> dict[str, str]:
    allowed_headers = {"content-type", "content-length", "server"}
    return {
        key: value
        for key, value in response.headers.items()
        if key.lower() in allowed_headers
    }
