"""Shared test fixtures."""

import base64

import httpx
import pytest
import respx


@pytest.fixture
def mock_api():
    """Provide a respx mock router for intercepting httpx requests."""
    with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture
def sample_audio_b64() -> str:
    """A minimal base64-encoded 'audio' payload for testing."""
    return base64.b64encode(b"\x00" * 100).decode()


@pytest.fixture
def tts_base_url() -> str:
    return "https://txt2sph.test.local"


@pytest.fixture
def stt_base_url() -> str:
    return "https://sph2txt.test.local"


@pytest.fixture
def sidon_base_url() -> str:
    return "https://sph2sphe.test.local"
