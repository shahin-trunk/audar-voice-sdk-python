"""Tests for voice resource operations."""

import httpx
import pytest
import respx

from audar import AsyncAudar
from audar.models.voice import (
    PersonaCreateRequest,
    PersonaDetail,
    PersonaListResponse,
    VoiceHealthResponse,
    VoiceProfile,
    VoiceSessionResponse,
)


BACKEND_BASE = "https://argent.test.local"


@pytest.fixture
def client():
    return AsyncAudar(
        api_key="test-key",
        tts_base_url="https://tts.test.local",
        stt_base_url="https://stt.test.local",
        sidon_base_url="https://sidon.test.local",
        backend_base_url=BACKEND_BASE,
    )


class TestVoiceSessions:
    @respx.mock
    async def test_create_session(self, client):
        respx.post(f"{BACKEND_BASE}/v1/voice/token").mock(
            return_value=httpx.Response(200, json={
                "token": "eyJhbGciOiJIUzI1NiJ9.test-token",
                "room_name": "voice-agent-abc12345",
                "livekit_url": "wss://livekitv2.audarai.com",
                "agent": {
                    "id": "6650a1b2c3d4e5f6a7b8c9d0",
                    "name": "Jasmine",
                    "voice": "Hope",
                    "asr_model": "flash",
                    "tts_model": "turbo",
                },
            })
        )

        session = await client.voice.create_session(
            persona_id="6650a1b2c3d4e5f6a7b8c9d0",
            voice="Hope",
            asr_model="flash",
            tts_model="turbo",
        )
        assert isinstance(session, VoiceSessionResponse)
        assert session.token.startswith("eyJ")
        assert session.room_name == "voice-agent-abc12345"
        assert session.livekit_url == "wss://livekitv2.audarai.com"
        assert session.agent.name == "Jasmine"
        assert session.agent.voice == "Hope"

    @respx.mock
    async def test_delete_session(self, client):
        respx.delete(f"{BACKEND_BASE}/v1/voice/session/voice-agent-abc12345").mock(
            return_value=httpx.Response(200, json={
                "status": "deleted",
                "room_name": "voice-agent-abc12345",
            })
        )

        await client.voice.delete_session("voice-agent-abc12345")


class TestVoiceProfiles:
    @respx.mock
    async def test_list_profiles(self, client):
        respx.get(f"{BACKEND_BASE}/v1/voice/profiles").mock(
            return_value=httpx.Response(200, json={
                "profiles": [
                    {
                        "id": "Hope",
                        "name": "Hope",
                        "language": "en",
                        "gender": "female",
                        "accent": "American",
                    },
                    {
                        "id": "Callum",
                        "name": "Callum",
                        "language": "en",
                        "gender": "male",
                        "accent": "British",
                    },
                ]
            })
        )

        profiles = await client.voice.list_profiles(language="en")
        assert len(profiles) == 2
        assert all(isinstance(p, VoiceProfile) for p in profiles)
        assert profiles[0].name == "Hope"
        assert profiles[1].gender == "male"

    @respx.mock
    async def test_list_profiles_filtered(self, client):
        route = respx.get(f"{BACKEND_BASE}/v1/voice/profiles").mock(
            return_value=httpx.Response(200, json={"profiles": []})
        )

        await client.voice.list_profiles(language="ar", gender="female")
        request = route.calls[0].request
        assert "language=ar" in str(request.url)
        assert "gender=female" in str(request.url)


class TestVoicePersonas:
    @respx.mock
    async def test_list_personas(self, client):
        respx.get(f"{BACKEND_BASE}/v1/personas").mock(
            return_value=httpx.Response(200, json={
                "personas": [
                    {
                        "id": "6650a1b2c3d4e5f6a7b8c9d0",
                        "name": "Jasmine",
                        "description": "A friendly assistant",
                        "gender": "female",
                        "language": "en",
                        "category": "general",
                        "is_active": True,
                        "is_default": True,
                        "created_at": "2024-01-01T00:00:00",
                    }
                ],
                "total": 1,
                "categories": ["general"],
            })
        )

        result = await client.voice.personas.list()
        assert isinstance(result, PersonaListResponse)
        assert result.total == 1
        assert result.personas[0].name == "Jasmine"

    @respx.mock
    async def test_get_persona(self, client):
        respx.get(f"{BACKEND_BASE}/v1/personas/6650a1b2c3d4e5f6a7b8c9d0").mock(
            return_value=httpx.Response(200, json={
                "id": "6650a1b2c3d4e5f6a7b8c9d0",
                "name": "Jasmine",
                "description": "Friendly assistant",
                "gender": "female",
                "language": "en",
                "category": "general",
                "tags": ["friendly", "general"],
                "default_voice": "en",
                "personality_traits": ["warm", "helpful"],
                "tone": "friendly",
                "system_prompt": "You are Jasmine.",
                "greeting_message": "Hi there!",
                "allow_interruptions": True,
                "enable_expressive_tags": True,
                "max_response_length": 256,
                "response_temperature": 0.7,
                "is_active": True,
                "is_default": True,
                "is_system": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "version": 1,
            })
        )

        persona = await client.voice.personas.get("6650a1b2c3d4e5f6a7b8c9d0")
        assert isinstance(persona, PersonaDetail)
        assert persona.name == "Jasmine"
        assert persona.system_prompt == "You are Jasmine."

    @respx.mock
    async def test_create_persona(self, client):
        respx.post(f"{BACKEND_BASE}/v1/personas").mock(
            return_value=httpx.Response(201, json={
                "id": "new-id-123",
                "name": "TestBot",
                "description": "A test bot",
                "gender": "neutral",
                "language": "en",
                "category": "general",
                "tags": [],
                "default_voice": "en",
                "personality_traits": [],
                "tone": "neutral",
                "system_prompt": "You are a test bot.",
                "allow_interruptions": True,
                "enable_expressive_tags": True,
                "max_response_length": 256,
                "response_temperature": 0.7,
                "is_active": True,
                "is_default": False,
                "is_system": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "version": 1,
            })
        )

        persona = await client.voice.personas.create(
            PersonaCreateRequest(
                name="TestBot",
                description="A test bot",
                system_prompt="You are a test bot.",
            )
        )
        assert persona.name == "TestBot"

    @respx.mock
    async def test_create_persona_from_dict(self, client):
        respx.post(f"{BACKEND_BASE}/v1/personas").mock(
            return_value=httpx.Response(201, json={
                "id": "new-id-456",
                "name": "DictBot",
                "description": "",
                "gender": "neutral",
                "language": "en",
                "category": "general",
                "tags": [],
                "default_voice": "en",
                "personality_traits": [],
                "tone": "neutral",
                "system_prompt": "",
                "allow_interruptions": True,
                "enable_expressive_tags": True,
                "max_response_length": 256,
                "response_temperature": 0.7,
                "is_active": True,
                "is_default": False,
                "is_system": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "version": 1,
            })
        )

        persona = await client.voice.personas.create({"name": "DictBot"})
        assert persona.name == "DictBot"

    @respx.mock
    async def test_delete_persona(self, client):
        respx.delete(f"{BACKEND_BASE}/v1/personas/some-id").mock(
            return_value=httpx.Response(204)
        )
        await client.voice.personas.delete("some-id")

    @respx.mock
    async def test_clone_persona(self, client):
        respx.post(f"{BACKEND_BASE}/v1/personas/source-id/clone").mock(
            return_value=httpx.Response(200, json={
                "id": "cloned-id",
                "name": "Jasmine Copy",
                "description": "Cloned from Jasmine",
                "gender": "female",
                "language": "en",
                "category": "general",
                "tags": [],
                "default_voice": "en",
                "personality_traits": [],
                "tone": "friendly",
                "system_prompt": "You are Jasmine.",
                "allow_interruptions": True,
                "enable_expressive_tags": True,
                "max_response_length": 256,
                "response_temperature": 0.7,
                "is_active": True,
                "is_default": False,
                "is_system": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "version": 1,
            })
        )

        cloned = await client.voice.personas.clone("source-id", "Jasmine Copy")
        assert cloned.name == "Jasmine Copy"


class TestVoiceHealth:
    @respx.mock
    async def test_health(self, client):
        respx.get(f"{BACKEND_BASE}/v1/voice/health").mock(
            return_value=httpx.Response(200, json={
                "status": "ready",
                "voice_enabled": True,
                "active_sessions": 2,
                "max_sessions": 10,
                "livekit_url": "wss://livekitv2.audarai.com",
            })
        )

        h = await client.voice.health()
        assert isinstance(h, VoiceHealthResponse)
        assert h.status == "ready"
        assert h.active_sessions == 2
        assert h.max_sessions == 10
