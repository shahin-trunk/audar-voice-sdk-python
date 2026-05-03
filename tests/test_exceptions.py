"""Tests for exception hierarchy and error parsing."""

import httpx
import pytest
import respx

from audar import (
    AsyncAudar,
    AuthenticationError,
    NotFoundError,
    ServerError,
    ServiceUnavailableError,
    ValidationError,
)
from audar._http import _parse_error_body


TTS_BASE = "https://txt2sph.test.local"


@pytest.fixture
def client():
    return AsyncAudar(
        api_key="test-key",
        tts_base_url=TTS_BASE,
        stt_base_url="https://stt.test.local",
        sidon_base_url="https://sidon.test.local",
    )


class TestErrorParsing:
    def test_flat_tts_format(self):
        body = {"error": "Speaker not found", "code": "speaker_not_found", "detail": "ID=xyz"}
        msg, code, detail, req_id = _parse_error_body(body)
        assert msg == "Speaker not found"
        assert code == "speaker_not_found"
        assert detail == "ID=xyz"
        assert req_id is None

    def test_sidon_nested_format(self):
        body = {
            "error": {
                "code": "AUDIO_TOO_LONG",
                "message": "Audio duration exceeds maximum",
                "detail": "Max: 30s",
                "request_id": "req_123",
            }
        }
        msg, code, detail, req_id = _parse_error_body(body)
        assert msg == "Audio duration exceeds maximum"
        assert code == "AUDIO_TOO_LONG"
        assert detail == "Max: 30s"
        assert req_id == "req_123"

    def test_elevenlabs_format(self):
        body = {"detail": {"status": "invalid_voice", "message": "Unknown voice_id"}}
        msg, code, detail, req_id = _parse_error_body(body)
        assert msg == "Unknown voice_id"
        assert code == "invalid_voice"

    def test_fastapi_default(self):
        body = {"detail": "Not Found"}
        msg, code, detail, req_id = _parse_error_body(body)
        assert msg == "Not Found"


class TestErrorMapping:
    @respx.mock
    async def test_401_raises_auth_error(self, client):
        respx.get(f"{TTS_BASE}/health").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid API key"})
        )
        with pytest.raises(AuthenticationError) as exc_info:
            await client.tts.health()
        assert exc_info.value.status_code == 401

    @respx.mock
    async def test_404_raises_not_found(self, client):
        respx.get(f"{TTS_BASE}/v1/speakers/nonexistent").mock(
            return_value=httpx.Response(
                404,
                json={"error": "Speaker not found", "code": "speaker_not_found"},
            )
        )
        with pytest.raises(NotFoundError) as exc_info:
            await client.tts.speakers.get("nonexistent")
        assert exc_info.value.error_code == "speaker_not_found"

    @respx.mock
    async def test_422_raises_validation_error(self, client):
        respx.post(f"{TTS_BASE}/elevenlabs/v1/text-to-speech/bad-id").mock(
            return_value=httpx.Response(
                422,
                json={"detail": {"status": "invalid_voice", "message": "Unknown voice_id: bad-id"}},
            )
        )
        with pytest.raises(ValidationError) as exc_info:
            await client.tts.elevenlabs_convert("bad-id", "hello")
        assert exc_info.value.error_code == "invalid_voice"

    @respx.mock
    async def test_503_raises_service_unavailable(self, client):
        respx.get(f"{TTS_BASE}/health").mock(
            return_value=httpx.Response(503, json={"detail": "Engine not initialized"})
        )
        with pytest.raises(ServiceUnavailableError):
            await client.tts.health()

    @respx.mock
    async def test_500_raises_server_error(self, client):
        respx.get(f"{TTS_BASE}/health").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )
        with pytest.raises(ServerError):
            await client.tts.health()
