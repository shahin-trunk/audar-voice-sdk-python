"""Tests for client initialization, auth, and context management."""

import os
from unittest.mock import patch

import pytest

from audar import AsyncAudar, Audar
from audar._config import AudarConfig
from audar._constants import DEFAULT_TTS_BASE_URL


class TestAudarConfig:
    def test_defaults(self):
        cfg = AudarConfig()
        assert cfg.api_key is None
        assert cfg.tts_base_url == "https://txt2sph.audarai.com"
        assert cfg.stt_base_url == "https://sph2txt.audarai.com"
        assert cfg.sidon_base_url == "https://sph2sphe.audarai.com"
        assert cfg.timeout == 60.0
        assert cfg.max_retries == 2

    def test_explicit_api_key(self):
        cfg = AudarConfig(api_key="test-key")
        assert cfg.api_key == "test-key"

    def test_env_api_key(self):
        with patch.dict(os.environ, {"AUDAR_API_KEY": "env-key"}):
            cfg = AudarConfig()
            assert cfg.api_key == "env-key"

    def test_explicit_overrides_env(self):
        with patch.dict(os.environ, {"AUDAR_API_KEY": "env-key"}):
            cfg = AudarConfig(api_key="explicit-key")
            assert cfg.api_key == "explicit-key"

    def test_trailing_slash_stripped(self):
        cfg = AudarConfig(tts_base_url="https://example.com/")
        assert cfg.tts_base_url == "https://example.com"


class TestAsyncAudarInit:
    def test_resources_created(self):
        client = AsyncAudar(api_key="test")
        assert client.tts is not None
        assert client.stt is not None
        assert client.audio is not None

    async def test_context_manager(self):
        async with AsyncAudar(api_key="test") as client:
            assert client.tts is not None

    def test_custom_urls(self):
        client = AsyncAudar(
            tts_base_url="https://custom-tts.example.com",
            stt_base_url="https://custom-stt.example.com",
            sidon_base_url="https://custom-sidon.example.com",
        )
        assert client.tts._base_url == "https://custom-tts.example.com"
        assert client.stt._base_url == "https://custom-stt.example.com"
        assert client.audio._base_url == "https://custom-sidon.example.com"


class TestSyncAudar:
    def test_resources_created(self):
        client = Audar(api_key="test")
        assert client.tts is not None
        assert client.stt is not None
        assert client.audio is not None
        client.close()

    def test_context_manager(self):
        with Audar(api_key="test") as client:
            assert client.tts is not None
