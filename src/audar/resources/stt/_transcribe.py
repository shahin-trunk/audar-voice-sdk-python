"""STT transcription operations: file, batch, SSE streaming."""

from __future__ import annotations

from pathlib import Path
from typing import Any, AsyncIterator

import httpx

from audar._http import raise_for_status, request_with_retry
from audar._utils import parse_sse, read_file_bytes
from audar.models.stt import STTStreamChunk, TranscriptionResponse


class AsyncTranscribe:
    """Async STT transcription operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str, max_retries: int) -> None:
        self._client = client
        self._base_url = base_url
        self._max_retries = max_retries

    async def transcribe(
        self,
        files: list[bytes | str | Path],
        *,
        language: str | None = None,
        context: str | None = None,
        forced_alignment: bool = False,
    ) -> list[TranscriptionResponse]:
        """Batch transcribe multiple audio files.

        ``files`` can be raw bytes, file path strings, or ``Path`` objects.
        """
        params: dict[str, Any] = {}
        if language is not None:
            params["language"] = language
        if context is not None:
            params["context"] = context
        if forced_alignment:
            params["forced_alignment"] = "true"

        multipart_files = []
        for f in files:
            content, name = read_file_bytes(f)
            multipart_files.append(("files", (name, content, "audio/wav")))

        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/v2/transcribe",
            files=multipart_files,
            params=params,
            max_retries=self._max_retries,
        )
        return [TranscriptionResponse.model_validate(item) for item in resp.json()]

    async def transcribe_file(
        self,
        file: bytes | str | Path,
        *,
        language: str | None = None,
        context: str | None = None,
        forced_alignment: bool = False,
    ) -> TranscriptionResponse:
        """Transcribe a single audio file."""
        content, name = read_file_bytes(file)

        data: dict[str, Any] = {}
        if language is not None:
            data["language"] = language
        if context is not None:
            data["context"] = context
        if forced_alignment:
            data["forced_alignment"] = "true"

        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/v2/transcribe/file",
            files={"file": (name, content, "audio/wav")},
            data=data,
            max_retries=self._max_retries,
        )
        return TranscriptionResponse.model_validate(resp.json())

    async def transcribe_file_stream(
        self,
        file: bytes | str | Path,
        *,
        language: str | None = None,
        context: str | None = None,
    ) -> AsyncIterator[STTStreamChunk]:
        """Transcribe with SSE streaming (yields partial results)."""
        content, name = read_file_bytes(file)

        data: dict[str, Any] = {"stream": "true"}
        if language is not None:
            data["language"] = language
        if context is not None:
            data["context"] = context

        async with self._client.stream(
            "POST",
            f"{self._base_url}/v2/transcribe/file",
            files={"file": (name, content, "audio/wav")},
            data=data,
        ) as response:
            raise_for_status(response)
            async for event_data in parse_sse(response):
                if "error" in event_data:
                    break
                yield STTStreamChunk.model_validate(event_data)
