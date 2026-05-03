"""Voice agent session and profile operations."""

from __future__ import annotations

from typing import Any

import httpx

from audar._http import request_with_retry
from audar.models.voice import (
    VoiceHealthResponse,
    VoiceProfile,
    VoiceProfilesResponse,
    VoiceSessionResponse,
)
from audar.resources.voice._personas import AsyncPersonas


class AsyncVoice:
    """Async voice agent client.

    Manages voice agent sessions, profiles, and personas.

    Usage::

        async with AsyncAudar(api_key="...") as client:
            # Create a voice session
            session = await client.voice.create_session(persona_id="...")
            # session.token → use with LiveKit client SDK
            # session.livekit_url → LiveKit server URL

            # List voice profiles
            profiles = await client.voice.list_profiles(language="en")

            # Persona management
            personas = await client.voice.personas.list()
    """

    def __init__(self, client: httpx.AsyncClient, base_url: str, max_retries: int) -> None:
        self._client = client
        self._base_url = base_url
        self._max_retries = max_retries
        self.personas = AsyncPersonas(client, base_url, max_retries)

    async def create_session(
        self,
        persona_id: str,
        *,
        voice: str | None = None,
        asr_model: str | None = None,
        tts_model: str | None = None,
        instructions: str | None = None,
        chat_id: str | None = None,
        user_identity: str | None = None,
    ) -> VoiceSessionResponse:
        """Create a voice agent session.

        Returns a token and room info for connecting via LiveKit client SDK.

        Args:
            persona_id: MongoDB ObjectId of the persona to use.
            voice: TTS voice ID override (uses persona default if omitted).
            asr_model: ASR model - 'flash' (fast) or 'turbo' (accurate).
            tts_model: TTS model - 'turbo' (fast) or 'pro' (quality).
            instructions: Custom system prompt override.
            chat_id: Link session to an existing text chat.
            user_identity: Custom user identity (auto-generated if omitted).

        Returns:
            VoiceSessionResponse with token, room_name, livekit_url, and agent info.
        """
        payload: dict[str, Any] = {"persona_id": persona_id}
        if voice is not None:
            payload["voice"] = voice
        if asr_model is not None:
            payload["asr_model"] = asr_model
        if tts_model is not None:
            payload["tts_model"] = tts_model
        if instructions is not None:
            payload["instructions"] = instructions
        if chat_id is not None:
            payload["chat_id"] = chat_id
        if user_identity is not None:
            payload["user_identity"] = user_identity

        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/v1/voice/token",
            json=payload,
            max_retries=self._max_retries,
        )
        return VoiceSessionResponse.model_validate(resp.json())

    async def delete_session(self, room_name: str) -> None:
        """Teardown a voice session by room name."""
        await request_with_retry(
            self._client,
            "DELETE",
            f"{self._base_url}/v1/voice/session/{room_name}",
            max_retries=self._max_retries,
        )

    async def list_profiles(
        self,
        *,
        language: str | None = None,
        gender: str | None = None,
    ) -> list[VoiceProfile]:
        """List available voice profiles.

        Args:
            language: Filter by language ('en', 'ar').
            gender: Filter by gender ('male', 'female').
        """
        params: dict[str, str] = {}
        if language is not None:
            params["language"] = language
        if gender is not None:
            params["gender"] = gender

        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._base_url}/v1/voice/profiles",
            params=params,
            max_retries=self._max_retries,
        )
        data = resp.json()
        return [VoiceProfile.model_validate(p) for p in data.get("profiles", [])]

    async def voice_catalog(
        self,
        *,
        language: str | None = None,
        gender: str | None = None,
    ) -> list[VoiceProfile]:
        """Get available voice profiles from the catalog (alternative endpoint)."""
        params: dict[str, str] = {}
        if language is not None:
            params["language"] = language
        if gender is not None:
            params["gender"] = gender

        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._base_url}/v1/voice-catalog",
            params=params,
            max_retries=self._max_retries,
        )
        data = resp.json()
        return [VoiceProfile.model_validate(v) for v in data.get("voices", [])]

    async def health(self) -> VoiceHealthResponse:
        """Check voice subsystem health."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._base_url}/v1/voice/health",
            max_retries=self._max_retries,
        )
        return VoiceHealthResponse.model_validate(resp.json())
