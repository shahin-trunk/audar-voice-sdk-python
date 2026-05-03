"""STT WebSocket real-time streaming transcription."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import websockets

from audar._exceptions import WebSocketClosedError, WebSocketError
from audar.models.stt import WSFinalEvent, WSPartialEvent, WSReadyEvent, WSSegmentEvent


class STTWebSocket:
    """WebSocket connection for real-time streaming transcription.

    Usage::

        async with client.stt.websocket(language="en") as ws:
            await ws.start()
            await ws.send_audio(pcm_chunk)
            async for event in ws.events():
                print(event.text)
            result = await ws.stop()
    """

    def __init__(
        self,
        url: str,
        *,
        language: str | None = None,
        context: str | None = None,
    ) -> None:
        params: dict[str, str] = {}
        if language is not None:
            params["language"] = language
        if context is not None:
            params["context"] = context

        # Build query string
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{qs}"

        self._url = url
        self._ws: Any = None
        self._ready_event: WSReadyEvent | None = None

    async def __aenter__(self) -> STTWebSocket:
        self._ws = await websockets.connect(self._url)
        # Wait for ready message
        raw = await self._ws.recv()
        data = json.loads(raw)
        if data.get("type") == "ready":
            self._ready_event = WSReadyEvent.model_validate(data)
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._ws:
            await self._ws.close()

    @property
    def session_id(self) -> str | None:
        return self._ready_event.session_id if self._ready_event else None

    async def start(
        self, *, format: str = "pcm_s16le", sample_rate_hz: int = 16000
    ) -> None:
        """Send start message to begin streaming."""
        if self._ws is None:
            raise WebSocketError("Not connected. Use 'async with' context manager.")
        await self._ws.send(json.dumps({
            "type": "start",
            "format": format,
            "sample_rate_hz": sample_rate_hz,
        }))

    async def send_audio(self, chunk: bytes) -> None:
        """Send a binary audio chunk (PCM s16le)."""
        if self._ws is None:
            raise WebSocketError("Not connected.")
        await self._ws.send(chunk)

    async def events(self) -> AsyncIterator[WSPartialEvent | WSSegmentEvent]:
        """Yield partial and segment events as they arrive.

        Stops when a ``final`` event is received or the connection closes.
        """
        if self._ws is None:
            raise WebSocketError("Not connected.")

        async for raw in self._ws:
            data = json.loads(raw)
            msg_type = data.get("type", "")

            if msg_type == "partial":
                yield WSPartialEvent.model_validate(data)
            elif msg_type == "segment":
                yield WSSegmentEvent.model_validate(data)
            elif msg_type == "final":
                return
            elif msg_type == "error":
                raise WebSocketError(
                    data.get("message", "Unknown error"),
                    error_code=data.get("code"),
                )
            # Ignore heartbeat, info, etc.

    async def stop(self) -> WSFinalEvent | None:
        """Send stop message and wait for the final transcript."""
        if self._ws is None:
            raise WebSocketError("Not connected.")

        await self._ws.send(json.dumps({"type": "stop"}))

        async for raw in self._ws:
            data = json.loads(raw)
            if data.get("type") == "final":
                return WSFinalEvent.model_validate(data)
            if data.get("type") == "error":
                raise WebSocketError(
                    data.get("message", "Unknown error"),
                    error_code=data.get("code"),
                )
        return None
