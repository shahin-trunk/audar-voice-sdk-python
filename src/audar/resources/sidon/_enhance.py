"""Sidon audio enhancement operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from audar._http import request_with_retry
from audar._utils import read_file_bytes
from audar.models.sidon import (
    EnhanceResult,
    FormatsResponse,
    ModelInfo,
    ModelListResponse,
    SidonHealthResponse,
)


class AsyncEnhance:
    """Async Sidon audio enhancement operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str, max_retries: int) -> None:
        self._client = client
        self._base_url = base_url
        self._max_retries = max_retries

    async def enhance(
        self,
        file: bytes | str | Path,
        *,
        response_format: str = "wav",
    ) -> EnhanceResult:
        """Enhance audio quality using the Sidon model.

        Returns ``EnhanceResult`` with ``.audio_bytes``, ``.duration``,
        ``.sample_rate``, and ``.format``.
        """
        content, name = read_file_bytes(file)

        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._base_url}/v1/audio/enhance",
            files={"file": (name, content)},
            data={"response_format": response_format},
            max_retries=self._max_retries,
        )

        duration_str = resp.headers.get("X-Audio-Duration")
        sample_rate_str = resp.headers.get("X-Audio-Sample-Rate")

        return EnhanceResult(
            audio_bytes=resp.content,
            duration=float(duration_str) if duration_str else None,
            sample_rate=int(sample_rate_str) if sample_rate_str else None,
            format=response_format,
        )

    async def list_models(self) -> ModelListResponse:
        """List available enhancement models."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._base_url}/v1/models",
            max_retries=self._max_retries,
        )
        return ModelListResponse.model_validate(resp.json())

    async def get_model(self, model_id: str = "sidon-v0.1") -> ModelInfo:
        """Get information about a specific model."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._base_url}/v1/models/{model_id}",
            max_retries=self._max_retries,
        )
        return ModelInfo.model_validate(resp.json())

    async def list_formats(self) -> FormatsResponse:
        """List supported audio formats."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._base_url}/v1/audio/formats",
            max_retries=self._max_retries,
        )
        return FormatsResponse.model_validate(resp.json())

    async def health(self) -> SidonHealthResponse:
        """Check Sidon service health."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._base_url}/health",
            max_retries=self._max_retries,
        )
        return SidonHealthResponse.model_validate(resp.json())
