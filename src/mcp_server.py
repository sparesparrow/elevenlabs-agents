"""
ElevenLabs MCP Server for MIA voice integration.
"""

import asyncio
import json
import logging
import tempfile
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import websockets
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    EmbeddedResource,
    ImageContent,
)
from pydantic import BaseModel, Field

from .elevenlabs_client import ElevenLabsClient, VoiceProfileManager

logger = logging.getLogger(__name__)


# Tool argument models
class ListVoices(BaseModel):
    """List available ElevenLabs voices."""
    pass


class GetVoiceDetails(BaseModel):
    """Get details of a specific voice."""
    voice_id: str = Field(..., description="Voice ID to get details for")


class GenerateSpeech(BaseModel):
    """Generate speech from text."""
    text: str = Field(..., description="Text to convert to speech")
    voice_id: str = Field(..., description="Voice ID to use")
    model_id: Optional[str] = Field(default="eleven_monolingual_v1", description="Model ID to use")
    stability: Optional[float] = Field(default=0.5, description="Voice stability (0.0-1.0)")
    similarity_boost: Optional[float] = Field(default=0.5, description="Similarity boost (0.0-1.0)")


class CreateVoiceProfile(BaseModel):
    """Create a voice profile for easy reuse."""
    name: str = Field(..., description="Profile name")
    voice_id: str = Field(..., description="Voice ID to associate with profile")
    stability: Optional[float] = Field(default=0.5, description="Voice stability setting")
    similarity_boost: Optional[float] = Field(default=0.5, description="Similarity boost setting")


class ListVoiceProfiles(BaseModel):
    """List saved voice profiles."""
    pass


class GenerateSpeechFromProfile(BaseModel):
    """Generate speech using a saved voice profile."""
    text: str = Field(..., description="Text to convert to speech")
    profile_name: str = Field(..., description="Name of the voice profile to use")


class MIAVoiceCommand(BaseModel):
    """Execute a voice command for MIA IoT control."""
    command: str = Field(..., description="Voice command text (e.g., 'turn on the lights')")
    voice_profile: Optional[str] = Field(default="default", description="Voice profile for response")


class GetMIAStatus(BaseModel):
    """Get MIA system status with voice feedback."""
    voice_profile: Optional[str] = Field(default="default", description="Voice profile for status readout")


# Tool enum
class ElevenLabsTools(str):
    """Available ElevenLabs MCP tools."""
    LIST_VOICES = "elevenlabs_list_voices"
    GET_VOICE_DETAILS = "elevenlabs_get_voice_details"
    GENERATE_SPEECH = "elevenlabs_generate_speech"
    CREATE_VOICE_PROFILE = "elevenlabs_create_voice_profile"
    LIST_VOICE_PROFILES = "elevenlabs_list_voice_profiles"
    GENERATE_SPEECH_FROM_PROFILE = "elevenlabs_generate_speech_from_profile"
    MIA_VOICE_COMMAND = "mia_voice_command"
    GET_MIA_STATUS = "mia_get_status_voice"


class MIAVoiceIntegration:
    """Integration between ElevenLabs and MIA system."""

    def __init__(self, mia_host: str = "localhost", mia_port: int = 8000):
        self.mia_host = mia_host
        self.mia_port = mia_port
        self.mia_base_url = f"http://{mia_host}:{mia_port}"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def execute_voice_command(self, command_text: str) -> Dict[str, Any]:
        """Execute a voice command through MIA."""
        try:
            # This would integrate with MIA's command processing
            # For now, we'll simulate command processing
            payload = {
                "command": command_text,
                "source": "voice",
                "timestamp": asyncio.get_event_loop().time()
            }

            response = await self.client.post(f"{self.mia_base_url}/voice-command", json=payload)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to execute voice command: {e}")
            return {"error": f"Failed to execute command: {e}"}

    async def get_mia_status(self) -> Dict[str, Any]:
        """Get MIA system status."""
        try:
            response = await self.client.get(f"{self.mia_base_url}/status")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get MIA status: {e}")
            return {"error": f"Failed to get status: {e}"}


async def serve(
    elevenlabs_api_key: Optional[str] = None,
    mia_host: str = "localhost",
    mia_port: int = 8000
) -> None:
    """Main MCP server function for ElevenLabs voice integration."""

    # Initialize clients
    elevenlabs_client = ElevenLabsClient(api_key=elevenlabs_api_key)
    voice_profiles = VoiceProfileManager()
    mia_integration = MIAVoiceIntegration(host=mia_host, port=mia_port)

    async with elevenlabs_client, mia_integration:
        server = Server("mcp-elevenlabs-mia")

        @server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available voice and MIA integration tools."""
            return [
                Tool(
                    name=ElevenLabsTools.LIST_VOICES,
                    description="List all available ElevenLabs voices",
                    inputSchema=ListVoices.schema(),
                ),
                Tool(
                    name=ElevenLabsTools.GET_VOICE_DETAILS,
                    description="Get detailed information about a specific voice",
                    inputSchema=GetVoiceDetails.schema(),
                ),
                Tool(
                    name=ElevenLabsTools.GENERATE_SPEECH,
                    description="Convert text to speech using ElevenLabs",
                    inputSchema=GenerateSpeech.schema(),
                ),
                Tool(
                    name=ElevenLabsTools.CREATE_VOICE_PROFILE,
                    description="Create a reusable voice profile with specific settings",
                    inputSchema=CreateVoiceProfile.schema(),
                ),
                Tool(
                    name=ElevenLabsTools.LIST_VOICE_PROFILES,
                    description="List all saved voice profiles",
                    inputSchema=ListVoiceProfiles.schema(),
                ),
                Tool(
                    name=ElevenLabsTools.GENERATE_SPEECH_FROM_PROFILE,
                    description="Generate speech using a saved voice profile",
                    inputSchema=GenerateSpeechFromProfile.schema(),
                ),
                Tool(
                    name=ElevenLabsTools.MIA_VOICE_COMMAND,
                    description="Execute a voice command to control MIA IoT devices",
                    inputSchema=MIAVoiceCommand.schema(),
                ),
                Tool(
                    name=ElevenLabsTools.GET_MIA_STATUS,
                    description="Get MIA system status with voice feedback",
                    inputSchema=GetMIAStatus.schema(),
                ),
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute voice and MIA integration commands."""

            try:
                match name:
                    case ElevenLabsTools.LIST_VOICES:
                        voices = await elevenlabs_client.get_voices()
                        voices_text = "\n".join([
                            f"- {voice['name']} (ID: {voice['voice_id']}, Category: {voice.get('category', 'unknown')})"
                            for voice in voices
                        ])
                        return [TextContent(
                            type="text",
                            text=f"Available voices:\n{voices_text}"
                        )]

                    case ElevenLabsTools.GET_VOICE_DETAILS:
                        voice_id = arguments["voice_id"]
                        voice_details = await elevenlabs_client.get_voice(voice_id)
                        if voice_details:
                            return [TextContent(
                                type="text",
                                text=f"Voice details:\n{json.dumps(voice_details, indent=2)}"
                            )]
                        else:
                            return [TextContent(
                                type="text",
                                text=f"Voice {voice_id} not found"
                            )]

                    case ElevenLabsTools.GENERATE_SPEECH:
                        text = arguments["text"]
                        voice_id = arguments["voice_id"]
                        model_id = arguments.get("model_id", "eleven_monolingual_v1")
                        stability = arguments.get("stability", 0.5)
                        similarity_boost = arguments.get("similarity_boost", 0.5)

                        voice_settings = {
                            "stability": stability,
                            "similarity_boost": similarity_boost
                        }

                        audio_data = await elevenlabs_client.generate_speech(
                            text, voice_id, model_id, voice_settings
                        )

                        if audio_data:
                            # Save audio to temporary file and return path
                            with tempfile.NamedTemporaryFile(
                                suffix=".mp3", delete=False
                            ) as temp_file:
                                temp_file.write(audio_data)
                                temp_path = temp_file.name

                            return [TextContent(
                                type="text",
                                text=f"Speech generated successfully. Audio saved to: {temp_path}\nText: '{text}'"
                            )]
                        else:
                            return [TextContent(
                                type="text",
                                text="Failed to generate speech"
                            )]

                    case ElevenLabsTools.CREATE_VOICE_PROFILE:
                        name = arguments["name"]
                        voice_id = arguments["voice_id"]
                        stability = arguments.get("stability", 0.5)
                        similarity_boost = arguments.get("similarity_boost", 0.5)

                        settings = {
                            "stability": stability,
                            "similarity_boost": similarity_boost
                        }

                        voice_profiles.create_profile(name, voice_id, settings)
                        return [TextContent(
                            type="text",
                            text=f"Voice profile '{name}' created with voice ID '{voice_id}'"
                        )]

                    case ElevenLabsTools.LIST_VOICE_PROFILES:
                        profiles = voice_profiles.list_profiles()
                        if profiles:
                            profiles_text = "\n".join([f"- {profile}" for profile in profiles])
                            return [TextContent(
                                type="text",
                                text=f"Saved voice profiles:\n{profiles_text}"
                            )]
                        else:
                            return [TextContent(
                                type="text",
                                text="No voice profiles saved yet"
                            )]

                    case ElevenLabsTools.GENERATE_SPEECH_FROM_PROFILE:
                        text = arguments["text"]
                        profile_name = arguments["profile_name"]

                        profile = voice_profiles.get_profile(profile_name)
                        if not profile:
                            return [TextContent(
                                type="text",
                                text=f"Voice profile '{profile_name}' not found"
                            )]

                        voice_id = profile["voice_id"]
                        settings = profile["settings"]

                        audio_data = await elevenlabs_client.generate_speech(
                            text, voice_id, "eleven_monolingual_v1", settings
                        )

                        if audio_data:
                            with tempfile.NamedTemporaryFile(
                                suffix=".mp3", delete=False
                            ) as temp_file:
                                temp_file.write(audio_data)
                                temp_path = temp_file.name

                            return [TextContent(
                                type="text",
                                text=f"Speech generated from profile '{profile_name}'. Audio saved to: {temp_path}\nText: '{text}'"
                            )]
                        else:
                            return [TextContent(
                                type="text",
                                text="Failed to generate speech from profile"
                            )]

                    case ElevenLabsTools.MIA_VOICE_COMMAND:
                        command = arguments["command"]
                        voice_profile = arguments.get("voice_profile", "default")

                        # Execute the voice command
                        result = await mia_integration.execute_voice_command(command)

                        # Generate voice response
                        response_text = f"Voice command executed: {command}"
                        if "error" not in result:
                            response_text += ". Command completed successfully."
                        else:
                            response_text += f". Error: {result['error']}"

                        # Generate speech response
                        profile = voice_profiles.get_profile(voice_profile)
                        if profile:
                            audio_data = await elevenlabs_client.generate_speech(
                                response_text, profile["voice_id"], "eleven_monolingual_v1", profile["settings"]
                            )
                            if audio_data:
                                with tempfile.NamedTemporaryFile(
                                    suffix=".mp3", delete=False
                                ) as temp_file:
                                    temp_file.write(audio_data)
                                    temp_path = temp_file.name
                                response_text += f"\nVoice response saved to: {temp_path}"

                        return [TextContent(
                            type="text",
                            text=response_text
                        )]

                    case ElevenLabsTools.GET_MIA_STATUS:
                        voice_profile = arguments.get("voice_profile", "default")

                        # Get MIA status
                        status = await mia_integration.get_mia_status()

                        # Format status for voice readout
                        if "error" in status:
                            status_text = f"MIA system status unavailable: {status['error']}"
                        else:
                            # Create a natural language status summary
                            status_text = "MIA system status: "
                            if status.get("healthy", False):
                                status_text += "System is healthy. "
                            else:
                                status_text += "System has issues. "

                            devices = status.get("devices", [])
                            status_text += f"{len(devices)} devices connected."

                        # Generate voice response
                        profile = voice_profiles.get_profile(voice_profile)
                        if profile:
                            audio_data = await elevenlabs_client.generate_speech(
                                status_text, profile["voice_id"], "eleven_monolingual_v1", profile["settings"]
                            )
                            if audio_data:
                                with tempfile.NamedTemporaryFile(
                                    suffix=".mp3", delete=False
                                ) as temp_file:
                                    temp_file.write(audio_data)
                                    temp_path = temp_file.name
                                status_text += f"\nVoice status saved to: {temp_path}"

                        return [TextContent(
                            type="text",
                            text=status_text
                        )]

                    case _:
                        raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

        # Create server options
        options = server.create_initialization_options()

        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, options, raise_exceptions=True)