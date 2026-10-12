# ElevenLabs Agents

Voice synthesis and AI agent integration for the MIA (Modular Integration Architecture) IoT control system.

## Overview

ElevenLabs Agents provides voice-first control and feedback for MIA IoT devices through:

- **Text-to-Speech (TTS)**: Convert system responses and sensor data to natural voice
- **Voice Commands**: Process voice input for device control
- **Voice Profiles**: Customizable voice settings and preferences
- **MCP Integration**: Model Context Protocol server for AI agent voice capabilities
- **MIA Integration**: Direct connection to MIA's FastAPI server for IoT control

## Features

### Voice Synthesis
- Multiple voice options from ElevenLabs
- Custom voice settings (stability, similarity boost)
- Voice profile management for consistent responses
- Audio file generation and streaming

### MIA Integration
- Voice command processing for IoT devices
- Voice feedback for system status and sensor readings
- Real-time voice responses to MIA events
- Natural language device control

### MCP Server Tools
- `elevenlabs_list_voices`: Browse available voices
- `elevenlabs_generate_speech`: Convert text to speech
- `elevenlabs_create_voice_profile`: Save voice configurations
- `mia_voice_command`: Execute voice commands on MIA devices
- `mia_get_status_voice`: Get system status with voice readout

## Installation

### From source
```bash
cd elevenlabs-agents
pip install -e .
```

### Using uv
```bash
cd elevenlabs-agents
uv pip install -e .
```

## Setup

### 1. ElevenLabs API Key
Get your API key from [ElevenLabs](https://elevenlabs.io) and set it:

```bash
export ELEVENLABS_API_KEY="your-api-key-here"
```

Or pass it as a command line argument.

### 2. MIA System
Ensure MIA is running and accessible (default: localhost:8000).

## Usage

### Command Line
```bash
# Basic usage
elevenlabs-mcp-server

# With custom settings
elevenlabs-mcp-server --elevenlabs-api-key "your-key" --mia-host "192.168.1.100"

# Full options
elevenlabs-mcp-server --help
```

### Claude Desktop Configuration
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "elevenlabs-mia": {
      "command": "elevenlabs-mcp-server",
      "args": ["--elevenlabs-api-key", "your-api-key"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Voice Commands
Once configured, you can use natural language commands like:

- "Turn on the living room lights"
- "What's the temperature in the bedroom?"
- "Set the thermostat to 72 degrees"
- "Check the security camera status"

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ AI Agent    │───▶│ ElevenLabs  │───▶│ MIA FastAPI │
│ (Claude)    │    │ MCP Server  │    │ Server      │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Voice       │    │ Voice       │    │ IoT         │
│ Synthesis   │    │ Profiles    │    │ Devices     │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Voice Profiles

Create and manage voice profiles for consistent responses:

```python
# Create a profile
profile = {
    "name": "helpful-assistant",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
    "settings": {
        "stability": 0.75,
        "similarity_boost": 0.8
    }
}
```

## Integration with MIA

### Voice Command Flow
1. User speaks command → AI agent processes
2. Agent calls `mia_voice_command` tool
3. ElevenLabs server forwards to MIA FastAPI
4. MIA executes command on devices
5. Response generated with voice feedback

### Status Readout
- Automatic voice announcements for system events
- Sensor data spoken aloud
- Device status updates
- Error condition alerts

## Configuration

### Environment Variables
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `MIA_HOST`: MIA server hostname (default: localhost)
- `MIA_PORT`: MIA server port (default: 8000)

### Voice Profile Storage
Voice profiles are stored in `~/.elevenlabs-mia/voice_profiles.json`

## API Reference

### ElevenLabs Client
```python
from elevenlabs_agents.src.elevenlabs_client import ElevenLabsClient

client = ElevenLabsClient(api_key="your-key")
voices = await client.get_voices()
audio = await client.generate_speech("Hello world", "voice-id")
```

### MIA Integration
```python
from elevenlabs_agents.src.mcp_server import MIAVoiceIntegration

mia = MIAVoiceIntegration(host="localhost", port=8000)
result = await mia.execute_voice_command("turn on lights")
```

## Development

### Testing
```bash
cd elevenlabs-agents
python -m pytest tests/
```

### Building
```bash
cd elevenlabs-agents
python -m build
```

## Examples

### Basic Voice Generation
```python
# Generate speech
audio_data = await elevenlabs.generate_speech(
    text="Hello, I'm your MIA voice assistant",
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
    voice_settings={"stability": 0.7, "similarity_boost": 0.8}
)

# Save to file
with open("response.mp3", "wb") as f:
    f.write(audio_data)
```

### MIA Voice Commands
```python
# Voice-controlled device
result = await mia.execute_voice_command("dim the lights to 50%")

# Voice status readout
status = await mia.get_mia_status()
# Speaks: "MIA system status: System is healthy. 5 devices connected."
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

## Voice Synthesis Module (`elevenlabs_agents`)

Standalone multi-engine TTS library with personas and dramatic speech effects, independent of the MCP server above.
A comprehensive voice synthesis library for ElevenLabs agents with multiple TTS engine support, dramatic speech effects, and persona-based voice characteristics.

### Features

#### 🎭 Voice Personas
- **Elliot Alderson**: Hesitant, anxious voice with dramatic pauses (from Mr. Robot)
- **Mr. Robot**: Commanding, intense voice with urgent delivery
- **fsociety**: Rebellious, cryptic voice with mysterious tone
- **Professional**: Clear, confident, neutral business voice
- **Friendly**: Warm, approachable, engaging conversational voice
- **Mysterious**: Enigmatic, intriguing, suspenseful narrative voice
- **Authoritative**: Firm, commanding, decisive leadership voice
- **Enthusiastic**: Energetic, excited, passionate motivational voice
- **Calm**: Soothing, relaxed, composed therapeutic voice

#### 🔊 Multiple TTS Engines
1. **ElevenLabs API** - Premium high-quality voice synthesis (requires API key)
2. **pyttsx3** - Cross-platform Python TTS with offline support
3. **espeak-ng** - High-quality open-source TTS with SSML support
4. **Google Text-to-Speech** - Web-based synthesis with natural voices
5. **Festival** - Classic academic TTS engine
6. **spd-say** - Speech dispatcher fallback for accessibility

#### ⚡ Advanced Features
- **Dramatic Speech Effects**: Emphasis, pauses, and timing based on urgency
- **Urgency Levels**: Low, normal, high, and critical speech patterns
- **SSML Support**: Rich text formatting for supported engines
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Fallback System**: Automatic engine selection with graceful degradation
- **Configurable Personas**: Custom voice characteristics per persona

### Installation

##### With All Dependencies
```bash
pip install -e ".[tts]"
```

#### System Dependencies

##### Linux (Ubuntu/Debian)
```bash
## espeak-ng and Festival
sudo apt-get install espeak-ng festival festvox-kallpc16k

## Speech dispatcher
sudo apt-get install speech-dispatcher
```

##### macOS
```bash
## Using Homebrew
brew install espeak-ng
```

### Quick Start

#### Basic Usage
```python
from elevenlabs_agents import VoiceSystem, VoicePersona

## Initialize voice system
voice = VoiceSystem()

## Speak with default professional voice
voice.speak("Hello, world!")

## Speak with Elliot persona
voice.speak("I think we have a problem.", VoicePersona.ELLIOT)

## Speak with high urgency
voice.speak("Critical system alert!", VoicePersona.MR_ROBOT, "critical")
```

#### ElevenLabs API Integration
```python
## Set API key
import os
os.environ['ELEVENLABS_API_KEY'] = 'your_api_key_here'

## Or pass directly
voice = VoiceSystem(elevenlabs_api_key='your_api_key')

## Use ElevenLabs voices
voice.speak("High-quality voice synthesis", VoicePersona.PROFESSIONAL)
```

#### CLI Usage
```bash
## Test voice system
elevenlabs-voice-test --test-voice

## List available engines
elevenlabs-voice-test --list-engines

## Speak text with specific persona
elevenlabs-voice-test --speak "Hello world" --persona mr_robot --urgency high

## Test specific engine
elevenlabs-voice-test --test-engine pyttsx3
```

### Voice Personas

| Persona | Style | Use Case | Pitch | Speed | Pause |
|---------|-------|----------|-------|-------|-------|
| **Elliot** | Hesitant, anxious | Technical alerts, warnings | 45 | 130 | 0.8s |
| **Mr. Robot** | Commanding, intense | Critical alerts, security | 65 | 160 | 0.3s |
| **fsociety** | Rebellious, cryptic | System breaches, hacks | 55 | 145 | 0.6s |
| **Professional** | Clear, confident | Business announcements | 50 | 150 | 0.4s |
| **Friendly** | Warm, engaging | User interactions | 52 | 140 | 0.5s |
| **Mysterious** | Enigmatic, suspenseful | Story narration | 48 | 135 | 0.7s |
| **Authoritative** | Firm, decisive | Leadership, commands | 58 | 155 | 0.4s |
| **Enthusiastic** | Energetic, excited | Motivational content | 62 | 165 | 0.3s |
| **Calm** | Soothing, relaxed | Therapeutic, guidance | 46 | 125 | 0.9s |

### TTS Engines

#### Engine Priority (Automatic Selection)
1. **ElevenLabs** - Best quality, requires API key and internet
2. **pyttsx3** - Good quality, offline, cross-platform
3. **espeak-ng** - High quality, offline, SSML support
4. **Google TTS** - Good quality, requires internet
5. **Festival** - Classic quality, offline
6. **spd-say** - Basic quality, accessibility focused

#### Manual Engine Selection
```python
from elevenlabs_agents import VoiceSystem, TTSEngine

## Force specific engine
voice = VoiceSystem(preferred_engine=TTSEngine.PYTTSX3)
voice.speak("Using pyttsx3 engine")
```

### Configuration

#### Custom Persona Configuration
```python
from elevenlabs_agents import VoiceSystem, VoicePersona, VoiceConfig

voice = VoiceSystem()

## Create custom configuration
custom_config = VoiceConfig(
    persona=VoicePersona.PROFESSIONAL,
    pitch=55,        # Voice pitch (0-100)
    speed=160,       # Speech speed (50-300 WPM)
    volume=85,       # Volume level (0-100)
    voice_variant="male_confident",
    dramatic_pause=0.5,
    # ElevenLabs specific
    elevenlabs_voice_id="custom_voice_id",
    elevenlabs_stability=0.8,
    elevenlabs_similarity=0.9
)

## Apply custom configuration
voice.set_persona_config(VoicePersona.PROFESSIONAL, custom_config)
```

#### Environment Variables
```bash
## ElevenLabs API key
export ELEVENLABS_API_KEY="your_api_key_here"

## Logging level
export ELEVENLABS_LOG_LEVEL="DEBUG"
```

### API Reference

#### VoiceSystem Class

##### Constructor
```python
VoiceSystem(preferred_engine=None, elevenlabs_api_key=None)
```

##### Methods
- `speak(text, persona=VoicePersona.PROFESSIONAL, urgency="normal", **kwargs)` - Speak text
- `get_available_engines()` - List available TTS engines
- `get_current_engine()` - Get currently selected engine
- `set_persona_config(persona, config)` - Update persona configuration
- `test_engine(engine)` - Test specific TTS engine

#### VoicePersona Enum
- `ELLIOT`, `MR_ROBOT`, `FSOCIETY`, `PROFESSIONAL`, `FRIENDLY`, `MYSTERIOUS`, `AUTHORITATIVE`, `ENTHUSIASTIC`, `CALM`

#### TTSEngine Enum
- `ELEVENLABS`, `PYTTSX3`, `ESPEAK_NG`, `GTTS`, `FESTIVAL`, `SPD_SAY`

### Testing

#### Run Tests
```bash
## Install test dependencies
pip install pytest

## Run all tests
pytest tests/

## Run specific test
pytest tests/test_voice_system.py::TestVoiceSystem::test_initialization
```

#### Voice Testing
```bash
## Test all personas
elevenlabs-voice-test --test-voice

## Test specific engine
elevenlabs-voice-test --test-engine elevenlabs
```

### Troubleshooting

#### Common Issues

##### No Audio Output
1. Check system audio settings
2. Verify TTS engines are installed:
   ```bash
   # Test espeak-ng
   espeak-ng "Test"

   # Test pyttsx3
   python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"
   ```

##### ElevenLabs API Issues
1. Verify API key is set:
   ```bash
   echo $ELEVENLABS_API_KEY
   ```
2. Check API key validity on ElevenLabs dashboard
3. Ensure internet connection for API calls

##### Import Errors
```bash
## Install missing dependencies
pip install requests pyttsx3 gtts pygame

## For system TTS engines
sudo apt-get install espeak-ng festival speech-dispatcher
```

#### Engine-Specific Issues

##### pyttsx3 on Linux
May require additional system packages:
```bash
sudo apt-get install libttspico-utils
```

##### espeak-ng SSML
Only basic SSML tags are supported. Check espeak-ng documentation for details.

##### Google TTS
Requires internet connection and pygame for audio playback.

### Development

#### Project Structure
```
elevenlabs-agents/
├── elevenlabs_agents/
│   ├── __init__.py          # Main module exports
│   ├── voice_system.py      # Core voice synthesis system
│   ├── voice_config.py      # Configuration classes
│   └── cli.py              # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_voice_system.py # Unit tests

└── README.md              # This file
```

#### Adding New Personas
1. Add to `VoicePersona` enum in `voice_config.py`
2. Create preset method in `PersonaPreset` class
3. Update `_load_persona_configs()` in `VoiceSystem`

#### Adding New TTS Engines
1. Add to `TTSEngine` enum
2. Implement `_speak_{engine}()` method in `VoiceSystem`
3. Update `_detect_available_engines()` method
4. Add to priority list in `_select_voice_engine()`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### License

MIT License - see LICENSE file for details.

### Acknowledgments

- Inspired by the Mr. Robot TV series
- Built on top of excellent open-source TTS projects
- ElevenLabs for premium voice synthesis API

---

*"I'm in." - Mr. Robot*