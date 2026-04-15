"""
Tests for the ElevenLabs MCP server module.

Covers:
- MIAVoiceIntegration HTTP client wrapper (happy path + HTTP error handling)
- Tool argument Pydantic models (defaults, required fields, validation)
- ElevenLabsTools enum string values (protocol stability)
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from pydantic import ValidationError

# Add repo root to path so `src` can be imported as a package
# (mcp_server.py uses a relative import `from .elevenlabs_client`).
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import (  # noqa: E402
    CloneVoice,
    CreateVoiceProfile,
    DeleteVoice,
    ElevenLabsTools,
    GenerateSpeech,
    GenerateSpeechFromProfile,
    GetMIAStatus,
    GetVoiceDetails,
    ListVoiceProfiles,
    ListVoices,
    MIAVoiceCommand,
    MIAVoiceIntegration,
    StreamSpeech,
)


class TestMIAVoiceIntegration:
    """MIAVoiceIntegration wraps a small HTTP API for the MIA system."""

    @pytest.fixture
    def integration(self):
        integ = MIAVoiceIntegration(mia_host="mia-test", mia_port=9000)
        # Replace the real httpx client with a mock
        integ.client = AsyncMock()
        return integ

    def test_base_url_is_composed_from_host_and_port(self, integration):
        assert integration.mia_base_url == "http://mia-test:9000"

    @pytest.mark.asyncio
    async def test_execute_voice_command_posts_to_mia(self, integration):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok", "action": "lights_on"}
        mock_response.raise_for_status.return_value = None
        integration.client.post.return_value = mock_response

        result = await integration.execute_voice_command("turn on the lights")

        assert result == {"status": "ok", "action": "lights_on"}
        integration.client.post.assert_called_once()
        url = integration.client.post.call_args[0][0]
        payload = integration.client.post.call_args[1]["json"]
        assert url == "http://mia-test:9000/voice-command"
        assert payload["command"] == "turn on the lights"
        assert payload["source"] == "voice"
        assert "timestamp" in payload

    @pytest.mark.asyncio
    async def test_execute_voice_command_returns_error_on_http_failure(self, integration):
        # Simulate httpx.HTTPError (any subclass)
        integration.client.post.side_effect = httpx.ConnectError("boom")

        result = await integration.execute_voice_command("turn on the lights")

        assert "error" in result
        assert "boom" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_voice_command_returns_error_on_http_status_error(self, integration):
        request = httpx.Request("POST", "http://mia-test:9000/voice-command")
        response = httpx.Response(500, request=request)
        integration.client.post.side_effect = httpx.HTTPStatusError(
            "server error", request=request, response=response
        )

        result = await integration.execute_voice_command("x")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_mia_status_returns_json(self, integration):
        mock_response = MagicMock()
        mock_response.json.return_value = {"healthy": True, "devices": [1, 2, 3]}
        mock_response.raise_for_status.return_value = None
        integration.client.get.return_value = mock_response

        status = await integration.get_mia_status()

        assert status == {"healthy": True, "devices": [1, 2, 3]}
        integration.client.get.assert_called_once_with("http://mia-test:9000/status")

    @pytest.mark.asyncio
    async def test_get_mia_status_returns_error_on_timeout(self, integration):
        integration.client.get.side_effect = httpx.TimeoutException("read timeout")

        result = await integration.get_mia_status()

        assert "error" in result
        assert "timeout" in result["error"].lower() or "read timeout" in result["error"]

    @pytest.mark.asyncio
    async def test_async_context_manager_closes_client(self):
        integ = MIAVoiceIntegration()
        integ.client = AsyncMock()
        async with integ as ctx:
            assert ctx is integ
        integ.client.aclose.assert_awaited_once()


class TestToolArgumentModels:
    """Pydantic models used for MCP tool argument validation."""

    def test_list_voices_accepts_empty(self):
        ListVoices()  # no fields; should not raise

    def test_list_voice_profiles_accepts_empty(self):
        ListVoiceProfiles()

    def test_get_voice_details_requires_voice_id(self):
        with pytest.raises(ValidationError):
            GetVoiceDetails()
        assert GetVoiceDetails(voice_id="abc").voice_id == "abc"

    def test_generate_speech_requires_text_and_voice_id(self):
        with pytest.raises(ValidationError):
            GenerateSpeech(text="hi")  # missing voice_id
        with pytest.raises(ValidationError):
            GenerateSpeech(voice_id="v")  # missing text

    def test_generate_speech_applies_defaults(self):
        model = GenerateSpeech(text="hi", voice_id="v")
        assert model.model_id == "eleven_monolingual_v1"
        assert model.stability == 0.5
        assert model.similarity_boost == 0.5

    def test_generate_speech_respects_overrides(self):
        model = GenerateSpeech(
            text="hi", voice_id="v", stability=0.9, similarity_boost=0.1, model_id="other"
        )
        assert model.stability == 0.9
        assert model.similarity_boost == 0.1
        assert model.model_id == "other"

    def test_stream_speech_optional_output_path(self):
        model = StreamSpeech(text="hi", voice_id="v")
        assert model.output_path is None
        with_path = StreamSpeech(text="hi", voice_id="v", output_path="/tmp/out.mp3")
        assert with_path.output_path == "/tmp/out.mp3"

    def test_clone_voice_requires_name_and_paths(self):
        with pytest.raises(ValidationError):
            CloneVoice(name="x")
        model = CloneVoice(name="x", audio_file_paths=["a.mp3", "b.mp3"])
        assert model.description == ""
        assert model.audio_file_paths == ["a.mp3", "b.mp3"]

    def test_delete_voice_requires_voice_id(self):
        with pytest.raises(ValidationError):
            DeleteVoice()
        assert DeleteVoice(voice_id="abc").voice_id == "abc"

    def test_create_voice_profile_requires_name_and_voice_id(self):
        with pytest.raises(ValidationError):
            CreateVoiceProfile(name="x")
        with pytest.raises(ValidationError):
            CreateVoiceProfile(voice_id="v")
        model = CreateVoiceProfile(name="x", voice_id="v")
        assert model.stability == 0.5

    def test_mia_voice_command_defaults_voice_profile(self):
        model = MIAVoiceCommand(command="turn on")
        assert model.voice_profile == "default"

    def test_get_mia_status_defaults_voice_profile(self):
        assert GetMIAStatus().voice_profile == "default"

    def test_generate_speech_from_profile_requires_both(self):
        with pytest.raises(ValidationError):
            GenerateSpeechFromProfile(text="hi")
        with pytest.raises(ValidationError):
            GenerateSpeechFromProfile(profile_name="p")
        GenerateSpeechFromProfile(text="hi", profile_name="p")


class TestElevenLabsToolsEnum:
    """Stability check on the tool name strings exposed over MCP."""

    def test_tool_name_strings(self):
        assert ElevenLabsTools.LIST_VOICES == "elevenlabs_list_voices"
        assert ElevenLabsTools.GET_VOICE_DETAILS == "elevenlabs_get_voice_details"
        assert ElevenLabsTools.GENERATE_SPEECH == "elevenlabs_generate_speech"
        assert ElevenLabsTools.STREAM_SPEECH == "elevenlabs_stream_speech"
        assert ElevenLabsTools.CLONE_VOICE == "elevenlabs_clone_voice"
        assert ElevenLabsTools.DELETE_VOICE == "elevenlabs_delete_voice"
        assert ElevenLabsTools.CREATE_VOICE_PROFILE == "elevenlabs_create_voice_profile"
        assert ElevenLabsTools.LIST_VOICE_PROFILES == "elevenlabs_list_voice_profiles"
        assert ElevenLabsTools.GENERATE_SPEECH_FROM_PROFILE == "elevenlabs_generate_speech_from_profile"
        assert ElevenLabsTools.MIA_VOICE_COMMAND == "mia_voice_command"
        assert ElevenLabsTools.GET_MIA_STATUS == "mia_get_status_voice"


if __name__ == "__main__":
    pytest.main([__file__])
