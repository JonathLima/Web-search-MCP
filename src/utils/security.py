from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

BLOCKED_DOMAIN_PATTERNS: list[str] = [
    r"^([a-z0-9-]{30,}\.)",       # Suspiciously long subdomains
    r"\.xyz$",                     # High-abuse TLD (optional, configurable)
    r"\.top$",                     # High-abuse TLD
    r"\.club$",                    # High-abuse TLD
    r"\.work$",                    # High-abuse TLD
    r"^localhost",
    r"^127\.",
    r"^10\.",
    r"^192\.168\.",
    r"^172\.(1[6-9]|2\d|3[01])\.",
    r"^\[::1\]",
    r"^169\.254\.",               # Link-local
    r"^0\.",                      # 0.0.0.0 range
]

BLOCKED_DOMAIN_REGEX = re.compile("|".join(BLOCKED_DOMAIN_PATTERNS), re.IGNORECASE)

ALLOWED_SCHEMES = {"http", "https"}

def validate_url(url: str) -> tuple[bool, str]:
    if not url or not url.strip():
        return False, "URL is empty"

    try:
        parsed = urlparse(url)
    except Exception as exc:
        return False, f"URL is not parseable: {exc}"

    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, (
            f"Invalid scheme '{parsed.scheme}'. Only http and https are allowed. "
            f"Blocked schemes: file, ftp, data, javascript, etc."
        )

    hostname = parsed.hostname
    if not hostname:
        return False, "URL has no hostname"

    is_blocked, reason = _check_blocked(hostname)
    if is_blocked:
        return False, reason

    return True, ""

def _check_blocked(hostname: str) -> tuple[bool, str]:
    hostname = hostname.lower()

    if BLOCKED_DOMAIN_REGEX.search(hostname):
        return True, f"Hostname '{hostname}' matches a blocked pattern"

    if hostname in ("localhost", "0.0.0.0"):
        return True, f"Hostname '{hostname}' is blocked (SSRF prevention)"

    if not _is_ip_safe(hostname):
        return True, f"Hostname '{hostname}' resolves to a private/reserved IP (SSRF prevention)"

    return False, ""

def _is_ip_safe(hostname: str) -> bool:
    import ipaddress
    import socket

    try:
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
    except (socket.gaierror, ValueError):
        return False

def get_blocked_domains_config() -> list[str]:
    import os

    env_value = os.environ.get("BLOCKED_DOMAINS", "").strip()
    if not env_value:
        return []
    return [d.strip().lower() for d in env_value.split(",") if d.strip()]

def is_domain_blocked(url: str) -> tuple[bool, str]:
    try:
        parsed = urlparse(url)
    except Exception:
        return True, "URL is not parseable"

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return True, "URL has no hostname"

    is_blocked, reason = _check_blocked(hostname)
    if is_blocked:
        return True, reason

    blocked_domains = get_blocked_domains_config()
    for blocked in blocked_domains:
        if hostname == blocked or hostname.endswith("." + blocked):
            return True, f"Domain '{hostname}' is in the blocked list"

    return False, ""

def filter_domains(
    urls: list[str],
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> list[str]:
    result = []

    include_set = {d.lower() for d in (include_domains or [])}
    exclude_set = {d.lower() for d in (exclude_domains or [])}

    for url in urls:
        try:
            hostname = (urlparse(url).hostname or "").lower()
        except Exception:
            continue

        if include_set:
            matched = False
            for inc in include_set:
                if hostname == inc or hostname.endswith("." + inc):
                    matched = True
                    break
            if not matched:
                continue

        if exclude_set:
            excluded = False
            for exc in exclude_set:
                if hostname == exc or hostname.endswith("." + exc):
                    excluded = True
                    break
            if excluded:
                continue

        result.append(url)

    return result
