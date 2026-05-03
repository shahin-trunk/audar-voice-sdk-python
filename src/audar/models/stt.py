"""STT request and response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    """Word-level timing information."""

    word: str
    start: float
    end: float


class SegmentTimestamp(BaseModel):
    """Segment-level timing with optional word timestamps."""

    text: str
    start: float
    end: float
    words: list[WordTimestamp] | None = None


class TranscriptionResponse(BaseModel):
    """Response from file transcription."""

    text: str
    language: str | None = None
    duration: float | None = None
    segments: list[SegmentTimestamp] | None = None
    processing_time: float | None = None


class STTStreamChunk(BaseModel):
    """A chunk from SSE streaming transcription."""

    text: str
    language: str | None = None


class STTHealthResponse(BaseModel):
    """STT service health information."""

    status: str
    version: str | None = None
    engine: str | None = None
    aligner_enabled: bool | None = None
    memory: dict | None = None


class WSReadyEvent(BaseModel):
    """WebSocket 'ready' event from server."""

    type: str = "ready"
    session_id: str | None = None
    language: str | None = None


class WSPartialEvent(BaseModel):
    """WebSocket 'partial' interim transcript."""

    type: str = "partial"
    text: str
    language: str | None = None
    segment: int | None = None


class WSSegmentEvent(BaseModel):
    """WebSocket 'segment' boundary event."""

    type: str = "segment"
    text: str
    language: str | None = None
    segment: int | None = None
    is_final: bool = False


class WSFinalEvent(BaseModel):
    """WebSocket 'final' result after stop."""

    type: str = "final"
    text: str
    language: str | None = None
    duration: float | None = None
    segments: int | None = None
