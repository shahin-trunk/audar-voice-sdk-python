"""Voice agent session and persona models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Voice session models
# ---------------------------------------------------------------------------


class VoiceSessionRequest(BaseModel):
    """Request to create a voice agent session."""

    persona_id: str = Field(..., description="Persona ID (MongoDB ObjectId)")
    voice: str | None = Field(default=None, description="TTS voice ID override")
    asr_model: str | None = Field(default=None, description="ASR model: 'flash' or 'turbo'")
    tts_model: str | None = Field(default=None, description="TTS model: 'turbo' or 'pro'")
    instructions: str | None = Field(default=None, description="Custom system prompt override")
    chat_id: str | None = Field(default=None, description="Link to existing text chat")
    user_identity: str | None = Field(default=None, description="Custom user identity")


class VoiceSessionAgent(BaseModel):
    """Agent info returned in session response."""

    id: str
    name: str
    voice: str
    asr_model: str
    tts_model: str


class VoiceSessionResponse(BaseModel):
    """Response from creating a voice agent session."""

    token: str = Field(..., description="LiveKit JWT token for joining the room")
    room_name: str = Field(..., description="LiveKit room name")
    livekit_url: str = Field(..., description="LiveKit WebSocket URL")
    agent: VoiceSessionAgent


# ---------------------------------------------------------------------------
# Voice profile models
# ---------------------------------------------------------------------------


class VoiceProfile(BaseModel):
    """A voice profile from the catalog."""

    id: str
    name: str
    language: str
    gender: str
    accent: str | None = None


class VoiceProfilesResponse(BaseModel):
    """Response from listing voice profiles."""

    profiles: list[VoiceProfile]


# ---------------------------------------------------------------------------
# Voice health
# ---------------------------------------------------------------------------


class VoiceHealthResponse(BaseModel):
    """Voice subsystem health."""

    status: str
    voice_enabled: bool | None = None
    active_sessions: int | None = None
    max_sessions: int | None = None
    livekit_url: str | None = None


# ---------------------------------------------------------------------------
# Persona models
# ---------------------------------------------------------------------------


class VoiceConfig(BaseModel):
    """Voice configuration for a persona."""

    voice_id: str
    language: str = "en"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    emotion: str | None = None


class PersonaSummary(BaseModel):
    """Persona summary for list views."""

    id: str
    name: str
    description: str
    gender: str
    language: str
    category: str
    is_active: bool
    is_default: bool
    avatar_url: str | None = None
    voice_agent_id: str | None = None
    created_at: str


class PersonaDetail(BaseModel):
    """Full persona detail."""

    id: str
    name: str
    description: str
    avatar_url: str | None = None
    voice_agent_id: str | None = None
    gender: str
    language: str
    category: str
    tags: list[str]
    voice_en: VoiceConfig | None = None
    voice_ar: VoiceConfig | None = None
    default_voice: str
    personality_traits: list[str]
    tone: str
    system_prompt: str
    greeting_message: str | None = None
    fallback_message: str | None = None
    allow_interruptions: bool
    enable_expressive_tags: bool
    max_response_length: int
    response_temperature: float
    is_active: bool
    is_default: bool
    is_system: bool
    created_by: str | None = None
    created_at: str
    updated_at: str
    version: int


class PersonaListResponse(BaseModel):
    """Response from listing personas."""

    personas: list[PersonaSummary]
    total: int
    categories: list[str]


class PersonaCreateRequest(BaseModel):
    """Request to create a persona."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    voice_agent_id: str | None = None
    gender: Literal["male", "female", "neutral"] = "neutral"
    language: str = "en"
    category: str = "general"
    tags: list[str] = Field(default_factory=list)
    voice_en: VoiceConfig | None = None
    voice_ar: VoiceConfig | None = None
    default_voice: str = "en"
    personality_traits: list[str] = Field(default_factory=list)
    tone: str = "neutral"
    system_prompt: str = ""
    greeting_message: str | None = None
    fallback_message: str | None = None
    allow_interruptions: bool = True
    enable_expressive_tags: bool = True
    max_response_length: int = 256
    response_temperature: float = 0.7


class PersonaUpdateRequest(BaseModel):
    """Request to update a persona (partial update)."""

    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None
    voice_agent_id: str | None = None
    gender: Literal["male", "female", "neutral"] | None = None
    language: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    voice_en: VoiceConfig | None = None
    voice_ar: VoiceConfig | None = None
    default_voice: str | None = None
    personality_traits: list[str] | None = None
    tone: str | None = None
    system_prompt: str | None = None
    greeting_message: str | None = None
    fallback_message: str | None = None
    allow_interruptions: bool | None = None
    enable_expressive_tags: bool | None = None
    max_response_length: int | None = Field(default=None, ge=50, le=512)
    response_temperature: float | None = Field(default=None, ge=0.0, le=1.0)
    is_active: bool | None = None


class PersonaVersionEntry(BaseModel):
    """A single version history entry."""

    version: int
    changed_at: str
    changed_by: str | None = None
    change_reason: str | None = None


class PersonaVersionsResponse(BaseModel):
    """Response from listing persona versions."""

    versions: list[PersonaVersionEntry]
    current_version: int
