"""Finite HTTP scenarios for the public portfolio demo; no outbound socket is used."""

import json
from urllib.parse import urlsplit

import httpx

from app.services.security import BlockedTargetError

DEMO_HOST = "demo.api-pulse.invalid"
DEMO_ORIGIN = f"https://{DEMO_HOST}"
DEMO_PATHS = frozenset({"/echo", "/status/404", "/status/500", "/redirect"})
DEMO_URLS = frozenset(f"{DEMO_ORIGIN}{path}" for path in DEMO_PATHS)
BLOCKED_URL = f"{DEMO_ORIGIN}/blocked"


def validate_demo_url(url: str) -> str:
    try:
        parsed = urlsplit(url.strip())
    except ValueError as exc:
        raise BlockedTargetError("Blocked target. Choose one of the demo scenarios.") from exc
    # Scheme and host are compared case-insensitively, as RFC 3986 requires; the path
    # stays case-sensitive so only the four listed scenarios match.
    if (
        parsed.scheme.lower() != "https"
        or parsed.hostname != DEMO_HOST
        or parsed.netloc.lower() != DEMO_HOST
        or parsed.path not in DEMO_PATHS
        or parsed.query
        or parsed.fragment
    ):
        raise BlockedTargetError("Blocked target. Choose one of the demo scenarios.")
    return f"{DEMO_ORIGIN}{parsed.path}"


def scenario_response(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/echo":
        body = json.loads(request.content) if request.content else None
        return httpx.Response(
            201 if request.method == "POST" else 200,
            json={"method": request.method, "body": body},
            request=request,
        )
    if path == "/redirect":
        return httpx.Response(302, headers={"location": f"{DEMO_ORIGIN}/echo"}, request=request)
    if path in {"/status/404", "/status/500"}:
        status = int(path.rsplit("/", 1)[1])
        return httpx.Response(status, json={"status": status, "scenario": "controlled"}, request=request)
    raise RuntimeError("Unrecognized controlled scenario")


def safe_summary(url: str, method: str, status_code: int | None) -> str:
    if status_code is None:
        return "Demo request did not receive a response."
    path = urlsplit(url).path
    return f"Demo {method} {path}: HTTP {status_code}"
