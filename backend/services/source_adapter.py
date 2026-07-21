from __future__ import annotations

import hashlib
import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


class SourceAdapterError(Exception):
    """Raised when a source cannot be safely fetched or parsed."""


@dataclass(frozen=True)
class SourceSnapshot:
    url: str
    content: str
    content_type: str
    etag: str | None
    last_modified: str | None
    sha256: str
    status_code: int


class SourceAdapter:
    """Fetches allowlisted HTTP sources with bounded, SSRF-aware behavior."""

    MAX_BYTES = 5 * 1024 * 1024
    ALLOWED_TYPES = {"application/json", "application/rss+xml", "application/atom+xml", "text/xml", "text/html"}

    def __init__(self, allowed_hosts: set[str] | None = None, timeout: float = 30.0):
        self.allowed_hosts = allowed_hosts or set()
        self.timeout = timeout

    def validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise SourceAdapterError("Source URLs must use HTTPS and include a hostname")
        if self.allowed_hosts and parsed.hostname not in self.allowed_hosts:
            raise SourceAdapterError("Source host is not allowlisted")
        try:
            addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            raise SourceAdapterError("Source hostname could not be resolved") from exc
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise SourceAdapterError("Source resolves to a private or reserved address")

    async def fetch(self, url: str, etag: str | None = None, last_modified: str | None = None) -> SourceSnapshot | None:
        self.validate_url(url)
        headers = {"Accept": ", ".join(sorted(self.ALLOWED_TYPES)), "User-Agent": "RegulatoryComplianceMonitor/1.0"}
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 304:
            return None
        if response.status_code in {429, 500, 502, 503, 504}:
            raise SourceAdapterError(f"Transient source response: {response.status_code}")
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
        if content_type not in self.ALLOWED_TYPES:
            raise SourceAdapterError(f"Unsupported source content type: {content_type or 'missing'}")
        if len(response.content) > self.MAX_BYTES:
            raise SourceAdapterError("Source response exceeds the configured size limit")
        content = response.text
        return SourceSnapshot(
            url=url,
            content=content,
            content_type=content_type,
            etag=response.headers.get("etag"),
            last_modified=response.headers.get("last-modified"),
            sha256=hashlib.sha256(response.content).hexdigest(),
            status_code=response.status_code,
        )
