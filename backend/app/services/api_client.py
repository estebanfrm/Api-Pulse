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
) -> ApiClientResult:
    start = perf_counter()
    try:
        with httpx.Client(
            timeout=settings.request_timeout_seconds,
            follow_redirects=False,
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
    except httpx.TimeoutException:
        return _failure(start, "Request timed out.")
    except httpx.ConnectError as exc:
        return _failure(start, f"Connection failed: {exc}")
    except httpx.HTTPError as exc:
        return _failure(start, f"HTTP client error: {exc}")
    except Exception as exc:
        return _failure(start, f"Unexpected request error: {exc}")


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
