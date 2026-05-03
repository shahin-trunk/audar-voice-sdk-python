"""SDK configuration."""

from __future__ import annotations

import os

from audar._constants import (
    AUDAR_API_KEY_ENV,
    DEFAULT_BACKEND_BASE_URL,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_SIDON_BASE_URL,
    DEFAULT_STT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_TTS_BASE_URL,
)


class AudarConfig:
    """Holds resolved SDK configuration."""

    __slots__ = (
        "api_key",
        "tts_base_url",
        "stt_base_url",
        "sidon_base_url",
        "backend_base_url",
        "timeout",
        "connect_timeout",
        "max_retries",
    )

    def __init__(
        self,
        *,
        api_key: str | None = None,
        tts_base_url: str = DEFAULT_TTS_BASE_URL,
        stt_base_url: str = DEFAULT_STT_BASE_URL,
        sidon_base_url: str = DEFAULT_SIDON_BASE_URL,
        backend_base_url: str = DEFAULT_BACKEND_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self.api_key = api_key or os.environ.get(AUDAR_API_KEY_ENV)
        self.tts_base_url = tts_base_url.rstrip("/")
        self.stt_base_url = stt_base_url.rstrip("/")
        self.sidon_base_url = sidon_base_url.rstrip("/")
        self.backend_base_url = backend_base_url.rstrip("/")
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_retries = max_retries
