"""Tests for TTS resource operations."""

import base64

import httpx
import pytest
import respx

from audar import AsyncAudar
from audar.models.tts import SpeakerInfo, SpeakerListResponse, SynthesisResponse


TTS_BASE = "https://txt2sph.test.local"
SAMPLE_AUDIO_B64 = base64.b64encode(b"\x00" * 100).decode()


@pytest.fixture
def client():
    return AsyncAudar(
        api_key="test-key",
        tts_base_url=TTS_BASE,
        stt_base_url="https://stt.test.local",
        sidon_base_url="https://sidon.test.local",
    )


class TestTTSSynthesis:
    @respx.mock
    async def test_synthesize(self, client):
        respx.post(f"{TTS_BASE}/v1/synthesize").mock(
            return_value=httpx.Response(200, json={
                "audio": SAMPLE_AUDIO_B64,
                "format": "opus",
                "sample_rate": 48000,
                "duration": 1.5,
                "tokens_generated": 100,
            })
        )

        result = await client.tts.synthesize(text="Hello", speaker_id="Hope")
        assert isinstance(result, SynthesisResponse)
        assert result.duration == 1.5
        assert result.tokens_generated == 100
        assert len(result.to_bytes()) == 100

    @respx.mock
    async def test_synthesize_to_bytes(self, client):
        respx.post(f"{TTS_BASE}/v1/synthesize").mock(
            return_value=httpx.Response(200, json={
                "audio": SAMPLE_AUDIO_B64,
                "format": "mp3",
                "sample_rate": 24000,
                "duration": 2.0,
                "tokens_generated": 200,
            })
        )

        audio = await client.tts.synthesize_to_bytes(text="Hello", speaker_id="Hope")
        assert isinstance(audio, bytes)
        assert len(audio) == 100

    @respx.mock
    async def test_batch_synthesize(self, client):
        from audar.models.tts import SynthesisRequest

        respx.post(f"{TTS_BASE}/v1/batch/synthesize").mock(
            return_value=httpx.Response(200, json={
                "results": [
                    {
                        "audio": SAMPLE_AUDIO_B64,
                        "format": "opus",
                        "sample_rate": 48000,
                        "duration": 1.0,
                        "tokens_generated": 50,
                    }
                ],
                "total_duration": 0.5,
            })
        )

        reqs = [SynthesisRequest(text="Hello")]
        result = await client.tts.batch_synthesize(reqs)
        assert len(result.results) == 1
        assert result.total_duration == 0.5

    @respx.mock
    async def test_encode(self, client):
        respx.post(f"{TTS_BASE}/v1/encode").mock(
            return_value=httpx.Response(200, json={
                "codes": [1, 2, 3],
                "duration": 5.0,
            })
        )

        result = await client.tts.encode(b"\x00" * 50)
        assert result.codes == [1, 2, 3]
        assert result.duration == 5.0


class TestTTSSpeakers:
    @respx.mock
    async def test_list_speakers(self, client):
        respx.get(f"{TTS_BASE}/v1/speakers").mock(
            return_value=httpx.Response(200, json={
                "speakers": [
                    {
                        "speaker_id": "Hope",
                        "name": "Hope",
                        "reference_text": "ref text",
                        "codes_length": 512,
                        "is_active": True,
                    }
                ],
                "total": 1,
            })
        )

        result = await client.tts.speakers.list()
        assert isinstance(result, SpeakerListResponse)
        assert result.total == 1
        assert result.speakers[0].speaker_id == "Hope"

    @respx.mock
    async def test_get_speaker(self, client):
        respx.get(f"{TTS_BASE}/v1/speakers/Hope").mock(
            return_value=httpx.Response(200, json={
                "speaker_id": "Hope",
                "name": "Hope",
                "reference_text": "ref",
                "codes_length": 512,
                "is_active": True,
            })
        )

        result = await client.tts.speakers.get("Hope")
        assert isinstance(result, SpeakerInfo)
        assert result.speaker_id == "Hope"

    @respx.mock
    async def test_create_speaker(self, client):
        respx.post(f"{TTS_BASE}/v1/speakers").mock(
            return_value=httpx.Response(200, json={
                "speaker_id": "new-voice",
                "name": "New Voice",
                "reference_text": "test transcript",
                "codes_length": 256,
                "is_active": True,
            })
        )

        result = await client.tts.speakers.create(
            "new-voice", b"\x00" * 100, "test transcript", name="New Voice"
        )
        assert result.speaker_id == "new-voice"

    @respx.mock
    async def test_delete_speaker(self, client):
        respx.delete(f"{TTS_BASE}/v1/speakers/test").mock(
            return_value=httpx.Response(200, json={"message": "deleted"})
        )

        await client.tts.speakers.delete("test")


class TestTTSElevenLabs:
    @respx.mock
    async def test_elevenlabs_convert(self, client):
        respx.post(
            f"{TTS_BASE}/elevenlabs/v1/text-to-speech/Fahco4VZzobUeiPqni1S"
        ).mock(
            return_value=httpx.Response(
                200, content=b"\xff\xfb\x90\x00" * 100, headers={"content-type": "audio/mpeg"}
            )
        )

        audio = await client.tts.elevenlabs_convert(
            "Fahco4VZzobUeiPqni1S", "Hello"
        )
        assert isinstance(audio, bytes)
        assert len(audio) > 0


class TestTTSHealth:
    @respx.mock
    async def test_health(self, client):
        respx.get(f"{TTS_BASE}/health").mock(
            return_value=httpx.Response(200, json={
                "status": "ok",
                "model": "tts_flash",
                "device": "cuda",
                "version": "1.0.0",
            })
        )

        h = await client.tts.health()
        assert h.status == "ok"
        assert h.model == "tts_flash"
