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