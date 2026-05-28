import socket

import pytest

from app.services import security
from app.services.security import BlockedTargetError, UrlFormatError, validate_public_url


def test_validate_public_url_rejects_missing_scheme() -> None:
    with pytest.raises(UrlFormatError) as exc_info:
        validate_public_url("api.github.com")

    assert "Invalid URL format" in str(exc_info.value)


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
def test_validate_public_url_blocks_unsafe_targets(url: str) -> None:
    with pytest.raises(BlockedTargetError) as exc_info:
        validate_public_url(url)

    assert "Blocked target" in str(exc_info.value)


def test_validate_public_url_accepts_hostname_when_resolved_ips_are_public(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_getaddrinfo(hostname: str, *args: object, **kwargs: object) -> list[tuple[object, ...]]:
        assert hostname == "api.example.com"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]

    monkeypatch.setattr(security.socket, "getaddrinfo", fake_getaddrinfo)

    assert validate_public_url("https://api.example.com/v1") == "https://api.example.com/v1"


def test_validate_public_url_blocks_hostname_when_dns_resolves_to_private_ip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_getaddrinfo(hostname: str, *args: object, **kwargs: object) -> list[tuple[object, ...]]:
        assert hostname == "internal.example.com"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.10", 443))]

    monkeypatch.setattr(security.socket, "getaddrinfo", fake_getaddrinfo)

    with pytest.raises(BlockedTargetError) as exc_info:
        validate_public_url("https://internal.example.com")

    assert "Blocked target" in str(exc_info.value)


def test_validate_public_url_rejects_unresolvable_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_getaddrinfo(hostname: str, *args: object, **kwargs: object) -> list[tuple[object, ...]]:
        raise socket.gaierror
