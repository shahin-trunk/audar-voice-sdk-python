"""ElevenLabs-compatible TTS endpoint."""

from __future__ import annotations

import httpx

from audar._http import raise_for_status, request_with_retry


class AsyncElevenLabsCompat:
    """Async ElevenLabs-compatible synthesis."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        api_key: str | None,
        max_retries: int,
    ) -> None:
        self._client = client
        self._base_url = base_url
        self._api_key = api_key
        self._max_retries = max_retries

    async def convert(self, voice_id: str, text: str) -> bytes:
        """Synthesize speech using the ElevenLabs-compatible endpoint.

        Returns raw MP3 audio bytes.
        """
        headers: dict[str, str] = {}
        if self._api_key:
            headers["xi-api-key"] = self._api_key

        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/elevenlabs/v1/text-to-speech/{voice_id}",
            json={"text": text},
            headers=headers,
            max_retries=self._max_retries,
        )
        return resp.content
