"""STT resource — composes transcription and WebSocket operations."""

from __future__ import annotations

import httpx

from audar._http import request_with_retry
from audar.models.stt import STTHealthResponse
from audar.resources.stt._transcribe import AsyncTranscribe
from audar.resources.stt._websocket import STTWebSocket


class AsyncSTT(AsyncTranscribe):
    """Async STT client combining all STT operations.

    Usage::

        async with AsyncAudar(api_key="...") as client:
            result = await client.stt.transcribe_file(Path("audio.wav"))
            print(result.text)
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        max_retries: int,
    ) -> None:
        super().__init__(client, base_url, max_retries)

    async def health(self) -> STTHealthResponse:
        """Check STT service health."""
        resp = await request_with_retry(
            self._client, "GET", f"{self._base_url}/v2/health", max_retries=self._max_retries
        )
        return STTHealthResponse.model_validate(resp.json())

    def websocket(
        self,
        *,
        language: str | None = None,
        context: str | None = None,
    ) -> STTWebSocket:
        """Create a WebSocket connection for real-time streaming.

        Usage::

            async with client.stt.websocket(language="en") as ws:
                await ws.start()
                await ws.send_audio(pcm_chunk)
                async for event in ws.events():
                    print(event.text)
                result = await ws.stop()
        """
        ws_url = self._base_url.replace("https://", "wss://").replace("http://", "ws://")
        return STTWebSocket(
            f"{ws_url}/v2/transcribe/ws",
            language=language,
            context=context,
        )
