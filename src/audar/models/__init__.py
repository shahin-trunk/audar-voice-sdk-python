"""Public model re-exports."""

from audar.models.enums import AudioFormat, SampleRate, SidonAudioFormat
from audar.models.sidon import (
    EnhanceResult,
    FormatsResponse,
    ModelInfo,
    ModelListResponse,
    SidonHealthResponse,
)
from audar.models.stt import (
    SegmentTimestamp,
    STTHealthResponse,
    STTStreamChunk,
    TranscriptionResponse,
    WordTimestamp,
    WSFinalEvent,
    WSPartialEvent,
    WSReadyEvent,
    WSSegmentEvent,
)
from audar.models.tts import (
    BatchSynthesisResponse,
    EncodeReferenceResponse,
    ErrorResponse,
    SpeakerInfo,
    SpeakerListResponse,
    StreamChunk,
    SynthesisRequest,
    SynthesisResponse,
    TTSHealthResponse,
)

__all__ = [
    # Enums
    "AudioFormat",
    "SampleRate",
    "SidonAudioFormat",
    # TTS
    "BatchSynthesisResponse",
    "EncodeReferenceResponse",
    "ErrorResponse",
    "SpeakerInfo",
    "SpeakerListResponse",
    "StreamChunk",
    "SynthesisRequest",
    "SynthesisResponse",
    "TTSHealthResponse",
    # STT
    "SegmentTimestamp",
    "STTHealthResponse",
    "STTStreamChunk",
    "TranscriptionResponse",
    "WordTimestamp",
    "WSFinalEvent",
    "WSPartialEvent",
    "WSReadyEvent",
    "WSSegmentEvent",
    # Sidon
    "EnhanceResult",
    "FormatsResponse",
    "ModelInfo",
    "ModelListResponse",
    "SidonHealthResponse",
]
