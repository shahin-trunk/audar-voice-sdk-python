"""TTS WebSocket streaming synthesis."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import websockets

from audar._exceptions import WebSocketAuthError, WebSocketClosedError, WebSocketError
from audar.models.tts import StreamChunk


class TTSWebSocket:
    """WebSocket connection for real-time streaming synthesis."""

    def __init__(self, url: str, api_key: str | None = None) -> None:
        self._url = url
        self._api_key = api_key
        self._ws: Any = None

    async def __aenter__(self) -> TTSWebSocket:
        self._ws = await websockets.connect(self._url)
        if self._api_key:
            await self._ws.send(json.dumps({"api_key": self._api_key}))
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._ws:
            await self._ws.close()

    async def synthesize(
        self,
        text: str,
        *,
        speaker_id: str | None = None,
        reference_codes: list[int] | None = None,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 1.0,
        max_tokens: int = 1500,
        output_format: str = "opus",
        sample_rate: int = 48000,
    ) -> AsyncIterator[StreamChunk]:
        """Send a synthesis request and yield audio chunks."""
        if self._ws is None:
            raise WebSocketError("Not connected. Use 'async with' context manager.")

        payload: dict[str, Any] = {
            "text": text,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "output_format": output_format,
            "sample_rate": sample_rate,
        }
        if speaker_id is not None:
            payload["speaker_id"] = speaker_id
        if reference_codes is not None:
            payload["reference_codes"] = reference_codes

        await self._ws.send(json.dumps(payload))

        async for raw in self._ws:
            data = json.loads(raw)
            msg_type = data.get("type", "")

            if msg_type == "done":
                return
            if msg_type == "error":
                raise WebSocketError(
                    data.get("error", "Unknown WebSocket error"),
                    error_code=data.get("code"),
                )
            if msg_type == "chunk":
                yield StreamChunk(
                    audio=data["audio"],
                    chunk_index=data.get("chunk_index", 0),
                    is_final=data.get("is_final", False),
                    tokens_so_far=data.get("tokens_so_far", 0),
                )
