"""TTS synthesis operations: synthesize, stream, batch, encode."""

from __future__ import annotations

from pathlib import Path
from typing import Any, AsyncIterator

import httpx

from audar._http import raise_for_status, request_with_retry
from audar._utils import decode_audio_base64, encode_audio_base64, parse_sse
from audar.models.tts import (
    BatchSynthesisResponse,
    EncodeReferenceResponse,
    StreamChunk,
    SynthesisRequest,
    SynthesisResponse,
)


class AsyncSynthesis:
    """Async TTS synthesis operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str, max_retries: int) -> None:
        self._client = client
        self._base_url = base_url
        self._max_retries = max_retries

    async def synthesize(
        self,
        text: str,
        *,
        speaker_id: str | None = None,
        reference_audio: bytes | None = None,
        reference_text: str | None = None,
        reference_codes: list[int] | None = None,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 1.0,
        max_tokens: int = 1500,
        seed: int | None = None,
        min_tokens: int | None = None,
        output_format: str = "opus",
        sample_rate: int = 48000,
        enable_chunking: bool = True,
    ) -> SynthesisResponse:
        """Synthesize speech from text.

        Returns the full ``SynthesisResponse`` with base64-encoded audio.
        Call ``.to_bytes()`` on the response to get raw audio bytes.
        """
        payload: dict[str, Any] = {
            "text": text,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": False,
            "output_format": output_format,
            "sample_rate": sample_rate,
            "enable_chunking": enable_chunking,
        }
        if speaker_id is not None:
            payload["speaker_id"] = speaker_id
        if reference_audio is not None:
            payload["reference_audio"] = encode_audio_base64(reference_audio)
        if reference_text is not None:
            payload["reference_text"] = reference_text
        if reference_codes is not None:
            payload["reference_codes"] = reference_codes
        if seed is not None:
            payload["seed"] = seed
        if min_tokens is not None:
            payload["min_tokens"] = min_tokens

        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/v1/synthesize",
            json=payload,
            max_retries=self._max_retries,
        )
        return SynthesisResponse.model_validate(resp.json())

    async def synthesize_to_bytes(self, text: str, **kwargs: Any) -> bytes:
        """Synthesize and return decoded audio bytes directly."""
        result = await self.synthesize(text, **kwargs)
        return result.to_bytes()

    async def stream(
        self,
        text: str,
        *,
        speaker_id: str | None = None,
        reference_audio: bytes | None = None,
        reference_text: str | None = None,
        reference_codes: list[int] | None = None,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 1.0,
        max_tokens: int = 1500,
        seed: int | None = None,
        min_tokens: int | None = None,
        output_format: str = "opus",
        sample_rate: int = 48000,
    ) -> AsyncIterator[StreamChunk]:
        """Stream synthesis results as chunks via SSE."""
        payload: dict[str, Any] = {
            "text": text,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": True,
            "output_format": output_format,
            "sample_rate": sample_rate,
        }
        if speaker_id is not None:
            payload["speaker_id"] = speaker_id
        if reference_audio is not None:
            payload["reference_audio"] = encode_audio_base64(reference_audio)
        if reference_text is not None:
            payload["reference_text"] = reference_text
        if reference_codes is not None:
            payload["reference_codes"] = reference_codes
        if seed is not None:
            payload["seed"] = seed
        if min_tokens is not None:
            payload["min_tokens"] = min_tokens

        async with self._client.stream(
            "POST",
            f"{self._base_url}/v1/synthesize",
            json=payload,
        ) as response:
            raise_for_status(response)
            async for data in parse_sse(response):
                if "error" in data:
                    break
                yield StreamChunk.model_validate(data)

    async def batch_synthesize(
        self, requests: list[SynthesisRequest]
    ) -> BatchSynthesisResponse:
        """Batch synthesis for multiple requests."""
        payload = {"requests": [r.model_dump() for r in requests]}
        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/v1/batch/synthesize",
            json=payload,
            max_retries=self._max_retries,
        )
        return BatchSynthesisResponse.model_validate(resp.json())

    async def encode(self, audio: bytes) -> EncodeReferenceResponse:
        """Encode reference audio to reusable codes.

        Accepts raw audio bytes; base64-encodes internally.
        """
        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/v1/encode",
            json={"audio": encode_audio_base64(audio)},
            max_retries=self._max_retries,
        )
        return EncodeReferenceResponse.model_validate(resp.json())
