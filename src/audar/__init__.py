"""Audar Python SDK — unified client for TTS, STT, and speech enhancement."""

from audar._client import AsyncAudar, Audar
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
    WebSocketAuthError,
    WebSocketClosedError,
    WebSocketError,
)

__all__ = [
    # Clients
    "AsyncAudar",
    "Audar",
    # Exceptions
    "AudarError",
    "AuthenticationError",
    "ConflictError",
    "ConnectionError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ServiceUnavailableError",
    "TimeoutError",
    "ValidationError",
    "WebSocketAuthError",
    "WebSocketClosedError",
    "WebSocketError",
]
