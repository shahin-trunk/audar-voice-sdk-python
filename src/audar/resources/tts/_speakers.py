"""TTS speaker management (CRUD)."""

from __future__ import annotations

from typing import Any

import httpx

from audar._http import request_with_retry
from audar._utils import encode_audio_base64
from audar.models.tts import SpeakerInfo, SpeakerListResponse


class AsyncSpeakers:
    """Async speaker management operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str, max_retries: int) -> None:
        self._client = client
        self._base_url = base_url
        self._max_retries = max_retries

    @property
    def _speakers_url(self) -> str:
        return f"{self._base_url}/v1/speakers"

    async def create(
        self,
        speaker_id: str,
        audio: bytes,
        text: str,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SpeakerInfo:
        """Register a new speaker for voice cloning.

        ``audio`` should be raw audio bytes (any supported format).
        """
        payload: dict[str, Any] = {
            "speaker_id": speaker_id,
            "audio": encode_audio_base64(audio),
            "text": text,
        }
        if name is not None:
            payload["name"] = name
        if metadata is not None:
            payload["metadata"] = metadata

        resp = await request_with_retry(
            self._client,
            "POST",
            self._speakers_url,
            json=payload,
            max_retries=self._max_retries,
        )
        return SpeakerInfo.model_validate(resp.json())

    async def list(self) -> SpeakerListResponse:
        """List all registered speakers."""
        resp = await request_with_retry(
            self._client,
            "GET",
            self._speakers_url,
            max_retries=self._max_retries,
        )
        return SpeakerListResponse.model_validate(resp.json())

    async def get(self, speaker_id: str) -> SpeakerInfo:
        """Get speaker information by ID."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._speakers_url}/{speaker_id}",
            max_retries=self._max_retries,
        )
        return SpeakerInfo.model_validate(resp.json())

    async def update(
        self,
        speaker_id: str,
        *,
        name: str | None = None,
        audio: bytes | None = None,
        text: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SpeakerInfo:
        """Update an existing speaker."""
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if audio is not None:
            payload["audio"] = encode_audio_base64(audio)
        if text is not None:
            payload["text"] = text
        if metadata is not None:
            payload["metadata"] = metadata

        resp = await request_with_retry(
            self._client,
            "PUT",
            f"{self._speakers_url}/{speaker_id}",
            json=payload,
            max_retries=self._max_retries,
        )
        return SpeakerInfo.model_validate(resp.json())

    async def delete(self, speaker_id: str) -> None:
        """Delete a registered speaker."""
        await request_with_retry(
            self._client,
            "DELETE",
            f"{self._speakers_url}/{speaker_id}",
            max_retries=self._max_retries,
        )

    async def disable(self, speaker_id: str) -> None:
        """Disable a speaker (soft delete)."""
        await request_with_retry(
            self._client,
            "POST",
            f"{self._speakers_url}/{speaker_id}/disable",
            max_retries=self._max_retries,
        )

    async def enable(self, speaker_id: str) -> SpeakerInfo:
        """Re-enable a disabled speaker."""
        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._speakers_url}/{speaker_id}/enable",
            max_retries=self._max_retries,
        )
        return SpeakerInfo.model_validate(resp.json())
