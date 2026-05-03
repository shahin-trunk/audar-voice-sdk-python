"""Exception hierarchy for the Audar SDK."""

from __future__ import annotations


class AudarError(Exception):
    """Base exception for all Audar SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        detail: str | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        self.request_id = request_id

    def __repr__(self) -> str:
        attrs = [f"message={self.message!r}"]
        if self.status_code is not None:
            attrs.append(f"status_code={self.status_code}")
        if self.error_code is not None:
            attrs.append(f"error_code={self.error_code!r}")
        return f"{type(self).__name__}({', '.join(attrs)})"


class AuthenticationError(AudarError):
    """Raised on 401 — invalid or missing API key."""


class RateLimitError(AudarError):
    """Raised on 429 — rate limited."""


class ValidationError(AudarError):
    """Raised on 400/422 — bad request body or invalid parameters."""


class NotFoundError(AudarError):
    """Raised on 404 — resource not found."""


class ConflictError(AudarError):
    """Raised on 409 — resource conflict (e.g. speaker already exists)."""


class ServiceUnavailableError(AudarError):
    """Raised on 503 — service not initialized or unavailable."""


class ServerError(AudarError):
    """Raised on 500 — internal server error."""


class ConnectionError(AudarError):
    """Raised on network failures, DNS resolution, etc."""


class TimeoutError(AudarError):
    """Raised when a request exceeds the configured timeout."""


class WebSocketError(AudarError):
    """Base for WebSocket-specific failures."""


class WebSocketAuthError(WebSocketError):
    """WebSocket authentication was rejected."""


class WebSocketClosedError(WebSocketError):
    """WebSocket connection closed unexpectedly."""
