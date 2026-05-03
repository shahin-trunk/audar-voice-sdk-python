<p align="center">
  <h1 align="center">Audar Voice SDK for Python</h1>
  <p align="center">
    <strong>Unified Python client for Audar's voice AI services</strong>
  </p>
  <p align="center">
    <a href="#installation">Installation</a> &nbsp;&bull;&nbsp;
    <a href="#quick-start">Quick Start</a> &nbsp;&bull;&nbsp;
    <a href="#text-to-speech">TTS</a> &nbsp;&bull;&nbsp;
    <a href="#speech-to-text">STT</a> &nbsp;&bull;&nbsp;
    <a href="#speech-enhancement">Enhancement</a> &nbsp;&bull;&nbsp;
    <a href="#voice-agents">Agents</a>
  </p>
</p>

---

The **Audar SDK** provides a clean, async-first Python interface to all Audar voice services — text-to-speech, speech-to-text, speech enhancement, and voice agent management — through a single, consistent API.

```python
from audar import AsyncAudar

async with AsyncAudar(api_key="sk-...") as client:
    audio = await client.tts.synthesize(text="Hello world", speaker_id="Hope")
    Path("hello.opus").write_bytes(audio.to_bytes())
```

### Highlights

- **Async-first** with full sync support — works everywhere
- **Four services, one client** — TTS, STT, Sidon, and Voice Agents
- **Pydantic models** for all requests and responses
- **Automatic retries** with exponential backoff on transient errors
- **Structured exceptions** with error codes from every service
- **Context manager** support for clean resource management

---

## Installation

```bash
pip install git+https://github.com/shahin-trunk/audar-voice-sdk-python.git
```

**Requirements:** Python 3.12+

**Dependencies** (installed automatically):
- `httpx` — async HTTP client
- `pydantic` — data validation
- `websockets` — WebSocket streaming

---

## Quick Start

### Async usage (recommended)

```python
import asyncio
from pathlib import Path
from audar import AsyncAudar

async def main():
    async with AsyncAudar(api_key="sk-...") as client:
        # Synthesize speech
        result = await client.tts.synthesize(
            text="Welcome to Audar.",
            speaker_id="Hope",
            output_format="mp3",
        )
        Path("welcome.mp3").write_bytes(result.to_bytes())
        print(f"Generated {result.duration:.1f}s of audio")

asyncio.run(main())
```

### Sync usage

```python
from audar import Audar

client = Audar(api_key="sk-...")
result = client.tts.synthesize(text="Hello", speaker_id="Hope")
print(f"Duration: {result.duration:.1f}s")
client.close()
```

### Configuration

```python
client = AsyncAudar(
    api_key="sk-...",                                    # or set AUDAR_API_KEY env var
    tts_base_url="https://txt2sph.audarai.com",         # TTS service
    stt_base_url="https://sph2txt.audarai.com",         # STT service
    sidon_base_url="https://sph2sphe.audarai.com",      # Speech enhancement
    backend_base_url="https://argent.audarai.com",      # Voice agents & personas
    timeout=60.0,                                        # Request timeout (seconds)
    max_retries=2,                                       # Retry on 429/503/connection errors
)
```

---

## Text-to-Speech

> `client.tts` — Speech synthesis, streaming, speaker management

### Synthesize speech

```python
result = await client.tts.synthesize(
    text="The weather today is beautiful.",
    speaker_id="Hope",                # Voice to use
    output_format="mp3",              # opus, wav, mp3, aac, ogg
    sample_rate=24000,                # 16000, 24000, 44100, 48000
    temperature=1.0,                  # Sampling temperature (0.0–2.0)
)

audio_bytes = result.to_bytes()       # Decoded audio
print(result.duration)                # Audio duration in seconds
print(result.tokens_generated)        # Tokens generated
```

### Stream synthesis (SSE)

```python
async for chunk in client.tts.stream(
    text="A long paragraph of text to stream in real-time...",
    speaker_id="Hope",
    output_format="opus",
):
    play_audio(chunk.to_bytes())      # Play each chunk as it arrives
    if chunk.is_final:
        print("Stream complete")
```

### Batch synthesis

```python
from audar.models import SynthesisRequest

requests = [
    SynthesisRequest(text="First sentence.", speaker_id="Hope"),
    SynthesisRequest(text="Second sentence.", speaker_id="Callum"),
]
batch = await client.tts.batch_synthesize(requests)
print(f"Batch completed in {batch.total_duration:.1f}s")
```

### Encode reference audio

```python
ref_audio = Path("reference.wav").read_bytes()
encoded = await client.tts.encode(ref_audio)
print(f"Encoded {encoded.duration:.1f}s into {len(encoded.codes)} codes")

# Use codes for synthesis
result = await client.tts.synthesize(
    text="Clone this voice.",
    reference_codes=encoded.codes,
)
```

### ElevenLabs-compatible endpoint

```python
mp3_bytes = await client.tts.elevenlabs_convert(
    voice_id="Fahco4VZzobUeiPqni1S",   # Callum
    text="Drop-in replacement for ElevenLabs API.",
)
```

### WebSocket streaming

```python
async with client.tts.websocket() as ws:
    async for chunk in ws.synthesize(text="Real-time synthesis", speaker_id="Hope"):
        play_audio(chunk.to_bytes())
```

### Speaker management

```python
# List all speakers
speakers = await client.tts.speakers.list()
for s in speakers.speakers:
    print(f"{s.speaker_id}: {s.name} (active={s.is_active})")

# Register a new speaker
ref_audio = Path("my_voice.wav").read_bytes()
speaker = await client.tts.speakers.create(
    speaker_id="my-voice",
    audio=ref_audio,
    text="This is the reference transcript for my voice.",
    name="My Custom Voice",
)

# Get, update, delete
info = await client.tts.speakers.get("my-voice")
await client.tts.speakers.update("my-voice", name="Updated Name")
await client.tts.speakers.disable("my-voice")     # Soft disable
await client.tts.speakers.enable("my-voice")       # Re-enable
await client.tts.speakers.delete("my-voice")       # Permanent delete
```

### Health check

```python
health = await client.tts.health()
print(f"TTS: {health.status} | Model: {health.model} | Device: {health.device}")
```

---

## Speech-to-Text

> `client.stt` — File transcription, streaming, real-time WebSocket

### Transcribe a single file

```python
result = await client.stt.transcribe_file(
    Path("recording.wav"),
    language="en",
    context="Meeting about quarterly results",
)
print(result.text)
print(f"Duration: {result.duration:.1f}s | Processing: {result.processing_time:.1f}s")

# Word-level timestamps
if result.segments:
    for seg in result.segments:
        print(f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text}")
```

### Batch transcribe multiple files

```python
results = await client.stt.transcribe(
    [Path("file1.wav"), Path("file2.mp3"), raw_audio_bytes],
    language="en",
    forced_alignment=True,     # Word-level timestamps
)
for r in results:
    print(f"{r.language}: {r.text}")
```

### SSE streaming transcription

```python
async for chunk in client.stt.transcribe_file_stream(
    Path("long_recording.wav"),
    language="en",
):
    print(chunk.text, end="", flush=True)
```

### Real-time WebSocket streaming

```python
async with client.stt.websocket(language="en") as ws:
    await ws.start(format="pcm_s16le", sample_rate_hz=16000)

    # Stream audio chunks from microphone
    for pcm_chunk in microphone_stream():
        await ws.send_audio(pcm_chunk)

        # Process partial results as they arrive
        async for event in ws.events():
            if event.type == "partial":
                print(f"\r  {event.text}", end="", flush=True)
            elif event.type == "segment":
                print(f"\n> {event.text}")

    # Finalize
    final = await ws.stop()
    print(f"\nFinal: {final.text} ({final.duration:.1f}s)")
```

### Health check

```python
health = await client.stt.health()
print(f"STT: {health.status} | Engine: {health.engine}")
```

---

## Speech Enhancement

> `client.audio` — Noise reduction and audio enhancement via Sidon

### Enhance audio

```python
result = await client.audio.enhance(
    Path("noisy_recording.wav"),
    response_format="wav",
)
Path("clean_recording.wav").write_bytes(result.audio_bytes)
print(f"Enhanced: {result.duration:.1f}s at {result.sample_rate}Hz")
```

### List models and formats

```python
# Available models
models = await client.audio.list_models()
for m in models.data:
    print(f"{m.id}: ready={m.ready}, max_duration={m.max_duration_seconds}s")

# Supported formats
formats = await client.audio.list_formats()
print(f"Input:  {formats.input_formats}")
print(f"Output: {formats.output_formats}")
```

### Health check

```python
health = await client.audio.health()
print(f"Sidon: {health.status} | Model loaded: {health.model_loaded}")
```

---

## Voice Agents

> `client.voice` — Voice agent sessions, profiles, and persona management

Voice agents provide real-time conversational AI over audio. The SDK manages session lifecycle and persona configuration; the actual audio stream uses [LiveKit's client SDK](https://docs.livekit.io/client-sdk-js/).

### Create a voice session

```python
session = await client.voice.create_session(
    persona_id="6650a1b2c3d4e5f6a7b8c9d0",
    voice="Hope",                    # Override persona's default voice
    asr_model="flash",               # 'flash' (fast) or 'turbo' (accurate)
    tts_model="turbo",               # 'turbo' (fast) or 'pro' (quality)
    instructions="Speak only French.",
)

print(session.token)                 # JWT for LiveKit client SDK
print(session.room_name)             # "voice-agent-abc12345"
print(session.livekit_url)           # "wss://livekitv2.audarai.com"
print(session.agent.name)            # "Jasmine"

# Connect using LiveKit client SDK with the token...
# When done:
await client.voice.delete_session(session.room_name)
```

### List voice profiles

```python
# All voices
profiles = await client.voice.list_profiles()

# Filtered
arabic_female = await client.voice.list_profiles(language="ar", gender="female")
for p in arabic_female:
    print(f"{p.id}: {p.name} ({p.accent})")
```

### Persona management

```python
# List personas
result = await client.voice.personas.list(
    category="support",
    language="en",
    active_only=True,
)
print(f"Found {result.total} personas in categories: {result.categories}")

# Get persona details
persona = await client.voice.personas.get("6650a1b2c3d4e5f6a7b8c9d0")
print(f"{persona.name}: {persona.system_prompt[:80]}...")

# Create a persona
from audar.models import PersonaCreateRequest, VoiceConfig

new_persona = await client.voice.personas.create(PersonaCreateRequest(
    name="Sales Assistant",
    description="Handles product inquiries",
    gender="female",
    language="en",
    category="sales",
    tags=["sales", "product", "english"],
    voice_en=VoiceConfig(voice_id="Hope", language="en"),
    personality_traits=["professional", "friendly", "knowledgeable"],
    tone="professional",
    system_prompt="You are a knowledgeable sales assistant...",
    greeting_message="Hi! How can I help you today?",
    response_temperature=0.7,
))

# Or create from a dict
persona = await client.voice.personas.create({
    "name": "Quick Bot",
    "system_prompt": "You are a helpful assistant.",
})

# Update
await client.voice.personas.update(persona.id, {
    "greeting_message": "Hey there! What can I do for you?",
    "tone": "casual",
})

# Clone
clone = await client.voice.personas.clone(persona.id, "Sales Assistant v2")

# Set as default
await client.voice.personas.set_default(persona.id)

# Version history
versions = await client.voice.personas.versions(persona.id)
print(f"Current version: {versions.current_version}")

# Restore a previous version
await client.voice.personas.restore(persona.id, version=2)

# Delete (soft-delete)
await client.voice.personas.delete(persona.id)
```

### Voice health

```python
health = await client.voice.health()
print(f"Voice: {health.status}")
print(f"Sessions: {health.active_sessions}/{health.max_sessions}")
```

---

## Error Handling

The SDK provides a structured exception hierarchy that normalizes errors from all services:

```python
from audar import (
    AudarError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServiceUnavailableError,
)

try:
    await client.tts.synthesize(text="Hello", speaker_id="nonexistent")
except NotFoundError as e:
    print(f"Not found: {e.message} (code={e.error_code})")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except ServiceUnavailableError:
    print("Service is still loading, try again shortly")
except AuthenticationError:
    print("Check your API key")
except AudarError as e:
    print(f"Unexpected error: {e.message} (status={e.status_code})")
```

**Exception hierarchy:**

| Exception | HTTP Status | When |
|-----------|------------|------|
| `AuthenticationError` | 401 | Invalid or missing API key |
| `ValidationError` | 400 / 422 | Bad request body or parameters |
| `NotFoundError` | 404 | Speaker, persona, or model not found |
| `ConflictError` | 409 | Resource already exists |
| `RateLimitError` | 429 | Too many requests |
| `ServerError` | 500 | Internal server error |
| `ServiceUnavailableError` | 503 | Service loading or unavailable |
| `TimeoutError` | — | Request exceeded timeout |
| `ConnectionError` | — | Network failure |
| `WebSocketError` | — | WebSocket-specific failure |

---

## API Reference

### Client constructors

| Class | Description |
|-------|-------------|
| `AsyncAudar(api_key, **opts)` | Async client — use with `async with` |
| `Audar(api_key, **opts)` | Sync wrapper — use with `with` |

### Resources

| Resource | Service | Access |
|----------|---------|--------|
| **TTS** | Text-to-Speech | `client.tts` |
| **STT** | Speech-to-Text | `client.stt` |
| **Audio** | Speech Enhancement (Sidon) | `client.audio` |
| **Voice** | Voice Agents & Personas | `client.voice` |

### TTS methods

| Method | Returns |
|--------|---------|
| `tts.synthesize(text, **opts)` | `SynthesisResponse` |
| `tts.synthesize_to_bytes(text, **opts)` | `bytes` |
| `tts.stream(text, **opts)` | `AsyncIterator[StreamChunk]` |
| `tts.batch_synthesize(requests)` | `BatchSynthesisResponse` |
| `tts.encode(audio)` | `EncodeReferenceResponse` |
| `tts.elevenlabs_convert(voice_id, text)` | `bytes` |
| `tts.websocket()` | `TTSWebSocket` |
| `tts.health()` | `TTSHealthResponse` |
| `tts.speakers.create(...)` | `SpeakerInfo` |
| `tts.speakers.list()` | `SpeakerListResponse` |
| `tts.speakers.get(id)` | `SpeakerInfo` |
| `tts.speakers.update(id, **opts)` | `SpeakerInfo` |
| `tts.speakers.delete(id)` | `None` |
| `tts.speakers.disable(id)` | `None` |
| `tts.speakers.enable(id)` | `SpeakerInfo` |

### STT methods

| Method | Returns |
|--------|---------|
| `stt.transcribe(files, **opts)` | `list[TranscriptionResponse]` |
| `stt.transcribe_file(file, **opts)` | `TranscriptionResponse` |
| `stt.transcribe_file_stream(file, **opts)` | `AsyncIterator[STTStreamChunk]` |
| `stt.websocket(**opts)` | `STTWebSocket` |
| `stt.health()` | `STTHealthResponse` |

### Audio methods

| Method | Returns |
|--------|---------|
| `audio.enhance(file, **opts)` | `EnhanceResult` |
| `audio.list_models()` | `ModelListResponse` |
| `audio.get_model(id)` | `ModelInfo` |
| `audio.list_formats()` | `FormatsResponse` |
| `audio.health()` | `SidonHealthResponse` |

### Voice methods

| Method | Returns |
|--------|---------|
| `voice.create_session(persona_id, **opts)` | `VoiceSessionResponse` |
| `voice.delete_session(room_name)` | `None` |
| `voice.list_profiles(**opts)` | `list[VoiceProfile]` |
| `voice.health()` | `VoiceHealthResponse` |
| `voice.personas.list(**opts)` | `PersonaListResponse` |
| `voice.personas.get(id)` | `PersonaDetail` |
| `voice.personas.create(request)` | `PersonaDetail` |
| `voice.personas.update(id, request)` | `PersonaDetail` |
| `voice.personas.delete(id)` | `None` |
| `voice.personas.clone(id, name)` | `PersonaDetail` |
| `voice.personas.set_default(id)` | `PersonaDetail` |
| `voice.personas.versions(id)` | `PersonaVersionsResponse` |
| `voice.personas.restore(id, version)` | `PersonaDetail` |

---

## Development

```bash
git clone https://github.com/shahin-trunk/audar-voice-sdk-python.git
cd audar-voice-sdk-python

pip install -e ".[test]"
pytest tests/ -v
```

---

## License

MIT
