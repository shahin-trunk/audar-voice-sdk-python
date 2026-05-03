"""TTS resource — composes synthesis, speakers, ElevenLabs compat, and WebSocket."""

from __future__ import annotations

import httpx

from audar._http import request_with_retry
from audar.models.tts import TTSHealthResponse
from audar.resources.tts._elevenlabs import AsyncElevenLabsCompat
from audar.resources.tts._speakers import AsyncSpeakers
from audar.resources.tts._synthesis import AsyncSynthesis
from audar.resources.tts._websocket import TTSWebSocket


class AsyncTTS(AsyncSynthesis):
    """Async TTS client combining all TTS operations.

    Usage::

        async with AsyncAudar(api_key="...") as client:
            result = await client.tts.synthesize(text="Hello", speaker_id="Hope")
            speakers = await client.tts.speakers.list()
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        api_key: str | None,
        max_retries: int,
    ) -> None:
        super().__init__(client, base_url, max_retries)
        self._api_key = api_key
        self.speakers = AsyncSpeakers(client, base_url, max_retries)
        self._elevenlabs = AsyncElevenLabsCompat(client, base_url, api_key, max_retries)

    async def health(self) -> TTSHealthResponse:
        """Check TTS service health."""
        resp = await request_with_retry(
            self._client, "GET", f"{self._base_url}/health", max_retries=self._max_retries
        )
        return TTSHealthResponse.model_validate(resp.json())

    async def elevenlabs_convert(self, voice_id: str, text: str) -> bytes:
        """Synthesize speech using the ElevenLabs-compatible endpoint.

        Returns raw MP3 bytes.
        """
        return await self._elevenlabs.convert(voice_id, text)

    def websocket(self) -> TTSWebSocket:
        """Create a WebSocket connection for real-time synthesis.

        Usage::

            async with client.tts.websocket() as ws:
                async for chunk in ws.synthesize(text="Hello", speaker_id="Hope"):
                    play(chunk.to_bytes())
        """
        ws_url = self._base_url.replace("https://", "wss://").replace("http://", "ws://")
        return TTSWebSocket(f"{ws_url}/v1/ws/synthesize", self._api_key)
