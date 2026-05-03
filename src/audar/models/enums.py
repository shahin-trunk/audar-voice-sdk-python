"""Shared enumerations for Audar SDK."""

from enum import Enum


class AudioFormat(str, Enum):
    """TTS audio output formats."""

    OPUS = "opus"
    WAV = "wav"
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"


class SampleRate(int, Enum):
    """Supported sample rates in Hz."""

    SR_16K = 16000
    SR_24K = 24000
    SR_44K = 44100
    SR_48K = 48000


class SidonAudioFormat(str, Enum):
    """Sidon audio formats (input and output)."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    OPUS = "opus"
    M4A = "m4a"
    WEBM = "webm"
