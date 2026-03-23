# Claude Code Integration Guide

This project ships an MCP server (`elevenlabs-mcp-server`) that exposes 11 voice and IoT tools directly inside Claude Code, Claude Desktop, and Cursor.

## Quick Setup

### 1. Install the package

```bash
pip install -e .
# or
uv pip install -e .
```

### 2. Set your API key

```bash
export ELEVENLABS_API_KEY="your-key-here"
```

### 3. Auto-config (Claude Code reads `.claude/settings.json`)

The `.claude/settings.json` in this repo already wires up the MCP server. Just open the project in Claude Code — the tools are immediately available.

---

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `elevenlabs_list_voices` | List all ElevenLabs voices |
| `elevenlabs_get_voice_details` | Get details for a specific voice |
| `elevenlabs_generate_speech` | TTS to temp MP3 file |
| `elevenlabs_stream_speech` | Real-time streaming TTS |
| `elevenlabs_clone_voice` | Clone a voice from audio samples |
| `elevenlabs_delete_voice` | Delete a cloned voice |
| `elevenlabs_create_voice_profile` | Save a reusable voice config |
| `elevenlabs_list_voice_profiles` | List saved profiles |
| `elevenlabs_generate_speech_from_profile` | TTS using a saved profile |
| `mia_voice_command` | Send voice command to MIA IoT system |
| `mia_get_status_voice` | Get MIA status as voice feedback |

---

## Example Claude Code Prompts

```
List all available voices and pick the best one for a British male assistant.
```

```
Clone my voice using the samples at ~/recordings/my_voice_1.mp3 and ~/recordings/my_voice_2.mp3,
then save it as a profile called "personal".
```

```
Generate speech for "The kitchen lights are now on" using the "assistant" voice profile
and play the file.
```

```
Stream the text "Good morning! Your 3 devices are all online." to voice ID 21m00Tcm4TlvDq8ikWAM
and save to /tmp/greeting.mp3
```

---

## Claude Code Hooks

To add voice announcements to your Claude Code sessions, add this to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "elevenlabs-mcp-server --speak 'Claude Code session started'"
          }
        ]
      }
    ]
  }
}
```

---

## Multi-MCP Composition

To combine this server with other MCP servers in Claude Desktop, see `examples/claude_desktop_config.json`.
