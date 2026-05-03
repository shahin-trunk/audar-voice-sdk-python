"""TTS request and response models."""

from __future__ import annotations

import base64
from typing import Any, Literal

from pydantic import BaseModel, Field

from audar.models.enums import AudioFormat


class SynthesisRequest(BaseModel):
    """Request body for speech synthesis."""

    text: str = Field(..., min_length=1, max_length=5000)
    speaker_id: str | None = None
    reference_audio: str | None = Field(default=None, description="Base64-encoded reference audio.")
    reference_text: str | None = None
    reference_codes: list[int] | None = None
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_k: int = Field(default=50, ge=1, le=1000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1500, ge=50, le=4096)
    seed: int | None = None
    min_tokens: int | None = Field(default=None, ge=1, le=1000)
    stream: bool = False
    output_format: AudioFormat = AudioFormat.OPUS
    sample_rate: Literal[16000, 24000, 44100, 48000] = 48000
    enable_chunking: bool = True


class SynthesisResponse(BaseModel):
    """Response from speech synthesis."""

    audio: str = Field(..., description="Base64-encoded audio data.")
    format: AudioFormat
    sample_rate: int
    duration: float
    tokens_generated: int

    def to_bytes(self) -> bytes:
        """Decode the base64 audio to raw bytes."""
        return base64.b64decode(self.audio)


class StreamChunk(BaseModel):
    """A single chunk from streaming synthesis."""

    audio: str
    chunk_index: int
    is_final: bool = False
    tokens_so_far: int = 0

    def to_bytes(self) -> bytes:
        """Decode the base64 audio chunk to raw bytes."""
        return base64.b64decode(self.audio)


class BatchSynthesisResponse(BaseModel):
    """Response from batch synthesis."""

    results: list[SynthesisResponse | ErrorResponse]
    total_duration: float


class EncodeReferenceResponse(BaseModel):
    """Response from encoding reference audio."""

    codes: list[int]
    duration: float


class SpeakerInfo(BaseModel):
    """Information about a registered speaker."""

    speaker_id: str
    name: str | None = None
    reference_text: str
    codes_length: int
    metadata: dict[str, Any] | None = None
    is_active: bool = True
    created_at: str | None = None
    updated_at: str | None = None


class SpeakerListResponse(BaseModel):
    """Response from listing speakers."""

    speakers: list[SpeakerInfo]
    total: int


class TTSHealthResponse(BaseModel):
    """TTS service health information."""

    status: str
    model: str | None = None
    device: str | None = None
    version: str | None = None


class ErrorResponse(BaseModel):
    """Error response from the TTS service."""

    error: str
    code: str = "internal_error"
    detail: str | None = None


# Resolve forward reference for BatchSynthesisResponse
BatchSynthesisResponse.model_rebuild()
