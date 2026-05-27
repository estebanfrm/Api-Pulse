import ipaddress
import socket
from urllib.parse import urlparse


class SecurityValidationError(ValueError):
    pass


class UrlFormatError(SecurityValidationError):
    pass


class BlockedTargetError(SecurityValidationError):
    pass


BLOCKED_HOSTNAMES = {"localhost"}
ALLOWED_SCHEMES = {"http", "https"}


def validate_public_url(url: str) -> str:
    candidate = url.strip()
    if not candidate:
        raise UrlFormatError("Invalid URL format. Enter a full http or https URL.")

    parsed = urlparse(candidate)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise UrlFormatError("Invalid URL format. Use a URL that starts with http:// or https://.")
    if not parsed.netloc:
        raise UrlFormatError("Invalid URL format. Include a hostname, for example https://api.example.com.")
    if not parsed.hostname:
        raise UrlFormatError("Invalid URL format. Include a valid hostname.")

    hostname = parsed.hostname.strip().lower()
    if hostname in BLOCKED_HOSTNAMES:
        raise BlockedTargetError("Blocked target. Localhost URLs are not allowed.")
    if hostname.endswith(".localhost"):
        raise BlockedTargetError("Blocked target. Localhost URLs are not allowed.")

    _validate_hostname_is_public(hostname)
    return parsed.geturl()


def _validate_hostname_is_public(hostname: str) -> None:
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        _validate_resolved_addresses(hostname)
        return

    _reject_private_address(ip)


def _validate_resolved_addresses(hostname: str) -> None:
    try:
        address_info = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UrlFormatError("Invalid URL target. Hostname could not be resolved.") from exc

    if not address_info:
        raise UrlFormatError("Invalid URL target. Hostname could not be resolved.")

    resolved_ips = {item[4][0] for item in address_info}
    for raw_ip in resolved_ips:
        try:
            ip = ipaddress.ip_address(raw_ip)
        except ValueError as exc:
            raise UrlFormatError("Invalid URL target. Hostname resolved to an invalid IP address.") from exc
        _reject_private_address(ip)


def _reject_private_address(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise BlockedTargetError("Blocked target. Private, local, reserved, or unsafe IP addresses are not allowed.")
