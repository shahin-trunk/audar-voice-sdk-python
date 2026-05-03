"""Audar SDK client classes: AsyncAudar (async) and Audar (sync wrapper)."""

from __future__ import annotations

import asyncio
import functools
import threading
from typing import Any

from audar._config import AudarConfig
from audar._constants import (
    DEFAULT_BACKEND_BASE_URL,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_SIDON_BASE_URL,
    DEFAULT_STT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_TTS_BASE_URL,
)
from audar._http import create_http_client
from audar.resources.sidon import AsyncSidon
from audar.resources.stt import AsyncSTT
from audar.resources.tts import AsyncTTS
from audar.resources.voice import AsyncVoice


class AsyncAudar:
    """Async client for Audar voice services.

    Usage::

        async with AsyncAudar(api_key="sk-...") as client:
            result = await client.tts.synthesize(text="Hello", speaker_id="Hope")
            transcript = await client.stt.transcribe_file(Path("audio.wav"))
            enhanced = await client.audio.enhance(Path("noisy.wav"))
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        tts_base_url: str = DEFAULT_TTS_BASE_URL,
        stt_base_url: str = DEFAULT_STT_BASE_URL,
        sidon_base_url: str = DEFAULT_SIDON_BASE_URL,
        backend_base_url: str = DEFAULT_BACKEND_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._config = AudarConfig(
            api_key=api_key,
            tts_base_url=tts_base_url,
            stt_base_url=stt_base_url,
            sidon_base_url=sidon_base_url,
            backend_base_url=backend_base_url,
            timeout=timeout,
            connect_timeout=connect_timeout,
            max_retries=max_retries,
        )
        self._client = create_http_client(self._config)

        self.tts = AsyncTTS(
            self._client,
            self._config.tts_base_url,
            self._config.api_key,
            self._config.max_retries,
        )
        self.stt = AsyncSTT(
            self._client,
            self._config.stt_base_url,
            self._config.max_retries,
        )
        self.audio = AsyncSidon(
            self._client,
            self._config.sidon_base_url,
            self._config.max_retries,
        )
        self.voice = AsyncVoice(
            self._client,
            self._config.backend_base_url,
            self._config.max_retries,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncAudar:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()


class _SyncResourceProxy:
    """Wraps an async resource so that every public async method can be called synchronously."""

    def __init__(self, async_resource: Any, loop: asyncio.AbstractEventLoop) -> None:
        self.__async = async_resource
        self.__loop = loop

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self.__async, name)
        if asyncio.iscoroutinefunction(attr):
            @functools.wraps(attr)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return self.__loop.run_until_complete(attr(*args, **kwargs))
            return wrapper
        # Sub-resources (e.g. tts.speakers)
        if hasattr(attr, "__dict__") and not isinstance(attr, (str, int, float, bool)):
            return _SyncResourceProxy(attr, self.__loop)
        return attr


class Audar:
    """Synchronous client for Audar voice services.

    Wraps ``AsyncAudar`` with a dedicated event loop running in a background thread.

    Usage::

        client = Audar(api_key="sk-...")
        result = client.tts.synthesize(text="Hello", speaker_id="Hope")
        print(result.duration)
        client.close()
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        tts_base_url: str = DEFAULT_TTS_BASE_URL,
        stt_base_url: str = DEFAULT_STT_BASE_URL,
        sidon_base_url: str = DEFAULT_SIDON_BASE_URL,
        backend_base_url: str = DEFAULT_BACKEND_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

        self._async_client = AsyncAudar(
            api_key=api_key,
            tts_base_url=tts_base_url,
            stt_base_url=stt_base_url,
            sidon_base_url=sidon_base_url,
            backend_base_url=backend_base_url,
            timeout=timeout,
            connect_timeout=connect_timeout,
            max_retries=max_retries,
        )

        self.tts = _SyncResourceProxy(self._async_client.tts, self._loop)
        self.stt = _SyncResourceProxy(self._async_client.stt, self._loop)
        self.audio = _SyncResourceProxy(self._async_client.audio, self._loop)
        self.voice = _SyncResourceProxy(self._async_client.voice, self._loop)

    def close(self) -> None:
        """Close the client and its background event loop."""
        asyncio.run_coroutine_threadsafe(
            self._async_client.close(), self._loop
        ).result(timeout=10)
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)

    def __enter__(self) -> Audar:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
