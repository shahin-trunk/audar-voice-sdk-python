"""Tests for Pydantic models."""

import base64

from audar.models.tts import (
    SpeakerInfo,
    SpeakerListResponse,
    StreamChunk,
    SynthesisResponse,
    TTSHealthResponse,
)
from audar.models.stt import (
    TranscriptionResponse,
    SegmentTimestamp,
    WordTimestamp,
    WSFinalEvent,
    WSPartialEvent,
)
from audar.models.sidon import (
    EnhanceResult,
    FormatsResponse,
    ModelInfo,
    ModelListResponse,
    SidonHealthResponse,
)
from audar.models.enums import AudioFormat, SampleRate, SidonAudioFormat


class TestTTSModels:
    def test_synthesis_response_to_bytes(self):
        raw = b"hello audio"
        resp = SynthesisResponse(
            audio=base64.b64encode(raw).decode(),
            format=AudioFormat.MP3,
            sample_rate=24000,
            duration=1.5,
            tokens_generated=100,
        )
        assert resp.to_bytes() == raw

    def test_stream_chunk_to_bytes(self):
        raw = b"chunk"
        chunk = StreamChunk(
            audio=base64.b64encode(raw).decode(),
            chunk_index=0,
        )
        assert chunk.to_bytes() == raw

    def test_speaker_info_roundtrip(self):
        info = SpeakerInfo(
            speaker_id="test-speaker",
            reference_text="Hello world",
            codes_length=512,
            name="Test",
            is_active=True,
        )
        data = info.model_dump()
        restored = SpeakerInfo.model_validate(data)
        assert restored.speaker_id == "test-speaker"
        assert restored.name == "Test"

    def test_speaker_list_response(self):
        resp = SpeakerListResponse(
            speakers=[
                SpeakerInfo(
                    speaker_id="s1",
                    reference_text="ref",
                    codes_length=10,
                )
            ],
            total=1,
        )
        assert resp.total == 1
        assert resp.speakers[0].speaker_id == "s1"

    def test_health_response(self):
        h = TTSHealthResponse(status="ok", model="tts_flash", device="cuda", version="1.0")
        assert h.status == "ok"


class TestSTTModels:
    def test_transcription_response(self):
        resp = TranscriptionResponse(
            text="Hello world",
            language="en",
            duration=5.2,
            segments=[
                SegmentTimestamp(
                    text="Hello world",
                    start=0.0,
                    end=5.2,
                    words=[
                        WordTimestamp(word="Hello", start=0.0, end=2.0),
                        WordTimestamp(word="world", start=2.5, end=5.2),
                    ],
                )
            ],
            processing_time=1.3,
        )
        assert resp.text == "Hello world"
        assert len(resp.segments) == 1
        assert len(resp.segments[0].words) == 2

    def test_ws_events(self):
        partial = WSPartialEvent(text="hello", language="en", segment=0)
        assert partial.type == "partial"

        final = WSFinalEvent(text="hello world", duration=3.0, segments=1)
        assert final.type == "final"


class TestSidonModels:
    def test_enhance_result(self):
        result = EnhanceResult(
            audio_bytes=b"enhanced",
            duration=2.5,
            sample_rate=48000,
            format="wav",
        )
        assert result.audio_bytes == b"enhanced"

    def test_model_info(self):
        info = ModelInfo(
            id="sidon-v0.1",
            owned_by="sarulab-speech",
            ready=True,
            max_duration_seconds=30.0,
            output_sample_rate=48000,
        )
        assert info.id == "sidon-v0.1"

    def test_model_list(self):
        ml = ModelListResponse(
            data=[ModelInfo(id="sidon-v0.1", ready=True)]
        )
        assert len(ml.data) == 1

    def test_formats_response(self):
        fr = FormatsResponse(
            input_formats=["wav", "mp3"],
            output_formats=["wav", "mp3", "flac"],
            default_output_format="wav",
        )
        assert "wav" in fr.input_formats

    def test_health(self):
        h = SidonHealthResponse(status="healthy", model_loaded=True, device="cuda")
        assert h.status == "healthy"


class TestEnums:
    def test_audio_format_values(self):
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.WAV.value == "wav"

    def test_sample_rate_values(self):
        assert SampleRate.SR_24K.value == 24000

    def test_sidon_format_values(self):
        assert SidonAudioFormat.FLAC.value == "flac"
        assert SidonAudioFormat.WEBM.value == "webm"
