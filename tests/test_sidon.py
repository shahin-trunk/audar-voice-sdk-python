"""Tests for Sidon resource operations."""

import httpx
import pytest
import respx

from audar import AsyncAudar
from audar.models.sidon import (
    EnhanceResult,
    FormatsResponse,
    ModelInfo,
    ModelListResponse,
    SidonHealthResponse,
)


SIDON_BASE = "https://sph2sphe.test.local"


@pytest.fixture
def client():
    return AsyncAudar(
        api_key="test-key",
        tts_base_url="https://tts.test.local",
        stt_base_url="https://stt.test.local",
        sidon_base_url=SIDON_BASE,
    )


class TestSidonEnhance:
    @respx.mock
    async def test_enhance(self, client):
        respx.post(f"{SIDON_BASE}/v1/audio/enhance").mock(
            return_value=httpx.Response(
                200,
                content=b"enhanced-audio-bytes",
                headers={
                    "X-Audio-Duration": "2.5",
                    "X-Audio-Sample-Rate": "48000",
                    "Content-Type": "audio/wav",
                },
            )
        )

        result = await client.audio.enhance(b"\x00" * 100, response_format="wav")
        assert isinstance(result, EnhanceResult)
        assert result.audio_bytes == b"enhanced-audio-bytes"
        assert result.duration == 2.5
        assert result.sample_rate == 48000
        assert result.format == "wav"


class TestSidonModels:
    @respx.mock
    async def test_list_models(self, client):
        respx.get(f"{SIDON_BASE}/v1/models").mock(
            return_value=httpx.Response(200, json={
                "object": "list",
                "data": [
                    {
                        "id": "sidon-v0.1",
                        "object": "model",
                        "owned_by": "sarulab-speech",
                        "ready": True,
                    }
                ],
            })
        )

        result = await client.audio.list_models()
        assert isinstance(result, ModelListResponse)
        assert len(result.data) == 1
        assert result.data[0].id == "sidon-v0.1"

    @respx.mock
    async def test_get_model(self, client):
        respx.get(f"{SIDON_BASE}/v1/models/sidon-v0.1").mock(
            return_value=httpx.Response(200, json={
                "id": "sidon-v0.1",
                "object": "model",
                "owned_by": "sarulab-speech",
                "ready": True,
                "max_duration_seconds": 30.0,
                "output_sample_rate": 48000,
                "supported_formats": ["wav", "mp3", "flac"],
            })
        )

        result = await client.audio.get_model("sidon-v0.1")
        assert isinstance(result, ModelInfo)
        assert result.ready is True
        assert result.max_duration_seconds == 30.0


class TestSidonFormats:
    @respx.mock
    async def test_list_formats(self, client):
        respx.get(f"{SIDON_BASE}/v1/audio/formats").mock(
            return_value=httpx.Response(200, json={
                "input_formats": ["wav", "mp3", "flac"],
                "output_formats": ["wav", "mp3", "flac", "ogg"],
                "default_output_format": "wav",
            })
        )

        result = await client.audio.list_formats()
        assert isinstance(result, FormatsResponse)
        assert "wav" in result.input_formats


class TestSidonHealth:
    @respx.mock
    async def test_health(self, client):
        respx.get(f"{SIDON_BASE}/health").mock(
            return_value=httpx.Response(200, json={
                "status": "healthy",
                "model_loaded": True,
                "device": "cuda",
                "version": "1.0.0",
            })
        )

        h = await client.audio.health()
        assert isinstance(h, SidonHealthResponse)
        assert h.status == "healthy"
        assert h.model_loaded is True
