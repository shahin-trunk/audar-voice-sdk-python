"""Internal utilities: SSE parsing, base64 helpers, file reading."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, AsyncIterator

import httpx


async def parse_sse(response: httpx.Response) -> AsyncIterator[dict[str, Any]]:
    """Parse Server-Sent Events from an httpx streaming response.

    Yields parsed JSON dicts from ``data:`` lines.
    Stops on ``data: [DONE]``.
    """
    async for line in response.aiter_lines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("data:"):
            payload = line[len("data:"):].strip()
            if payload == "[DONE]":
                return
            try:
                yield json.loads(payload)
            except json.JSONDecodeError:
                continue


def encode_audio_base64(audio: bytes) -> str:
    """Base64-encode raw audio bytes."""
    return base64.b64encode(audio).decode("ascii")


def decode_audio_base64(data: str) -> bytes:
    """Decode base64-encoded audio to raw bytes."""
    return base64.b64decode(data)


def read_file_bytes(file: bytes | str | Path) -> tuple[bytes, str]:
    """Read file content and determine a filename.

    Returns (content_bytes, filename).
    """
    if isinstance(file, bytes):
        return file, "audio.wav"
    path = Path(file)
    return path.read_bytes(), path.name
