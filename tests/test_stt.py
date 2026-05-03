"""Tests for STT resource operations."""

import httpx
import pytest
import respx

from audar import AsyncAudar
from audar.models.stt import TranscriptionResponse, STTHealthResponse


STT_BASE = "https://sph2txt.test.local"


@pytest.fixture
def client():
    return AsyncAudar(
        api_key="test-key",
        tts_base_url="https://tts.test.local",
        stt_base_url=STT_BASE,
        sidon_base_url="https://sidon.test.local",
    )


class TestSTTTranscribe:
    @respx.mock
    async def test_transcribe_batch(self, client):
        respx.post(f"{STT_BASE}/v2/transcribe").mock(
            return_value=httpx.Response(200, json=[
                {
                    "text": "Hello world",
                    "language": "en",
                    "duration": 5.2,
                    "segments": [],
                    "processing_time": 1.0,
                }
            ])
        )

        results = await client.stt.transcribe([b"\x00" * 100])
        assert len(results) == 1
        assert results[0].text == "Hello world"

    @respx.mock
    async def test_transcribe_file(self, client):
        respx.post(f"{STT_BASE}/v2/transcribe/file").mock(
            return_value=httpx.Response(200, json={
                "text": "Single file result",
                "language": "en",
                "duration": 3.0,
                "processing_time": 0.8,
            })
        )

        result = await client.stt.transcribe_file(b"\x00" * 100, language="en")
        assert isinstance(result, TranscriptionResponse)
        assert result.text == "Single file result"

    @respx.mock
    async def test_transcribe_with_params(self, client):
        route = respx.post(f"{STT_BASE}/v2/transcribe").mock(
            return_value=httpx.Response(200, json=[
                {"text": "result", "language": "de"}
            ])
        )

        await client.stt.transcribe(
            [b"\x00" * 100],
            language="de",
            context="meeting about AI",
            forced_alignment=True,
        )

        request = route.calls[0].request
        assert "language=de" in str(request.url)
        assert "forced_alignment=true" in str(request.url)


class TestSTTHealth:
    @respx.mock
    async def test_health(self, client):
        respx.get(f"{STT_BASE}/v2/health").mock(
            return_value=httpx.Response(200, json={
                "status": "ready",
                "version": "v2",
                "engine": "vLLM LLM",
                "aligner_enabled": False,
            })
        )

        h = await client.stt.health()
        assert isinstance(h, STTHealthResponse)
        assert h.status == "ready"
