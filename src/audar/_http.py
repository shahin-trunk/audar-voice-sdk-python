"""Shared HTTP client factory, auth injection, error parsing, and retry logic."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from audar._config import AudarConfig
from audar._constants import USER_AGENT
from audar._exceptions import (
    AudarError,
    AuthenticationError,
    ConflictError,
    ConnectionError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)

_STATUS_MAP: dict[int, type[AudarError]] = {
    401: AuthenticationError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
    503: ServiceUnavailableError,
}


def create_http_client(config: AudarConfig) -> httpx.AsyncClient:
    """Create a configured ``httpx.AsyncClient``."""
    headers: dict[str, str] = {"User-Agent": USER_AGENT}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    return httpx.AsyncClient(
        headers=headers,
        timeout=httpx.Timeout(config.timeout, connect=config.connect_timeout),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    )


def _parse_error_body(body: Any) -> tuple[str, str | None, str | None, str | None]:
    """Extract (message, error_code, detail, request_id) from various error formats.

    Handles three server formats:
    - TTS/STT flat:  {"error": "...", "code": "...", "detail": "..."}
    - Sidon nested:  {"error": {"code": "...", "message": "...", "detail": "...", "request_id": "..."}}
    - ElevenLabs:    {"detail": {"status": "...", "message": "..."}}
    """
    if not isinstance(body, dict):
        return str(body), None, None, None

    # Sidon nested format
    err = body.get("error")
    if isinstance(err, dict):
        return (
            err.get("message", "Unknown error"),
            err.get("code"),
            err.get("detail"),
            err.get("request_id"),
        )

    # ElevenLabs compat format
    det = body.get("detail")
    if isinstance(det, dict):
        return (
            det.get("message", "Unknown error"),
            det.get("status"),
            None,
            None,
        )

    # TTS/STT flat format
    if isinstance(err, str):
        return err, body.get("code"), body.get("detail"), None

    # FastAPI default {"detail": "string"}
    if isinstance(det, str):
        return det, None, None, None

    return str(body), None, None, None


def raise_for_status(response: httpx.Response) -> None:
    """Raise an appropriate ``AudarError`` subclass for non-2xx responses."""
    if response.is_success:
        return

    status = response.status_code
    try:
        body = response.json()
    except Exception:
        body = response.text

    message, error_code, detail, request_id = _parse_error_body(body)

    exc_cls = _STATUS_MAP.get(status)
    if exc_cls is None:
        exc_cls = ServerError if status >= 500 else ValidationError

    raise exc_cls(
        message,
        status_code=status,
        error_code=error_code,
        detail=detail,
        request_id=request_id,
    )


async def request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    max_retries: int = 2,
    **kwargs: Any,
) -> httpx.Response:
    """Send an HTTP request with retry on 429, 503, and connection errors."""
    last_exc: Exception | None = None

    for attempt in range(1 + max_retries):
        try:
            response = await client.request(method, url, **kwargs)
            if response.status_code in (429, 503) and attempt < max_retries:
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue
            raise_for_status(response)
            return response
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            last_exc = exc
            if attempt < max_retries:
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue
            raise ConnectionError(
                str(exc), error_code="connection_error"
            ) from exc
        except httpx.TimeoutException as exc:
            last_exc = exc
            if attempt < max_retries:
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue
            raise TimeoutError(
                str(exc), error_code="timeout"
            ) from exc

    raise ConnectionError(
        f"Request failed after {max_retries + 1} attempts: {last_exc}",
        error_code="max_retries_exceeded",
    )
