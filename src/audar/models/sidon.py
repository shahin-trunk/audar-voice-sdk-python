"""Sidon (speech enhancement) request and response models."""

from __future__ import annotations

from pydantic import BaseModel

from audar.models.enums import SidonAudioFormat


class EnhanceResult(BaseModel):
    """Result of audio enhancement.

    ``audio_bytes`` contains the raw enhanced audio data.
    """

    audio_bytes: bytes
    duration: float | None = None
    sample_rate: int | None = None
    format: str | None = None


class ModelInfo(BaseModel):
    """Information about a Sidon model."""

    id: str
    object: str = "model"
    owned_by: str | None = None
    ready: bool = True
    max_duration_seconds: float | None = None
    output_sample_rate: int | None = None
    supported_formats: list[str] | None = None


class ModelListResponse(BaseModel):
    """Response from listing Sidon models."""

    object: str = "list"
    data: list[ModelInfo]


class FormatsResponse(BaseModel):
    """Supported audio formats."""

    input_formats: list[str]
    output_formats: list[str]
    default_output_format: str = "wav"


class SidonHealthResponse(BaseModel):
    """Sidon service health information."""

    status: str
    model_loaded: bool | None = None
    device: str | None = None
    version: str | None = None
    checkpoint_repo: str | None = None
