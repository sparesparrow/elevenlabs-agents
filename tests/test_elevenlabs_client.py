"""
Tests for ElevenLabs client functionality.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from elevenlabs_client import ElevenLabsClient, VoiceProfileManager  # noqa: E402


class TestElevenLabsClient:
    """Test ElevenLabs API client."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        client = ElevenLabsClient(api_key="test-key")
        # Mock the httpx client
        client.client = AsyncMock()
        yield client
        await client.client.aclose()

    @pytest.mark.asyncio
    async def test_get_voices_success(self, client):
        """Test successful voice listing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "voices": [
                {"name": "Test Voice", "voice_id": "test-123", "category": "premade"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        client.client.get.return_value = mock_response

        voices = await client.get_voices()

        assert len(voices) == 1
        assert voices[0]["name"] == "Test Voice"
        client.client.get.assert_called_once_with("/v1/voices")

    @pytest.mark.asyncio
    async def test_generate_speech_success(self, client):
        """Test successful speech generation."""
        mock_response = MagicMock()
        mock_response.content = b"fake-audio-data"
        mock_response.raise_for_status.return_value = None
        client.client.post.return_value = mock_response

        audio = await client.generate_speech("Hello world", "voice-123")

        assert audio == b"fake-audio-data"
        client.client.post.assert_called_once()
        call_args = client.client.post.call_args
        assert call_args[0][0] == "/v1/text-to-speech/voice-123"
        assert "text" in call_args[1]["json"]
        assert call_args[1]["json"]["text"] == "Hello world"

    @pytest.mark.asyncio
    async def test_generate_speech_with_settings(self, client):
        """Test speech generation with custom voice settings."""
        mock_response = MagicMock()
        mock_response.content = b"audio-data"
        mock_response.raise_for_status.return_value = None
        client.client.post.return_value = mock_response

        await client.generate_speech(
            "Test", "voice-123", "model-456",
            {"stability": 0.8, "similarity_boost": 0.7}
        )

        call_args = client.client.post.call_args
        payload = call_args[1]["json"]
        assert payload["model_id"] == "model-456"
        assert payload["voice_settings"]["stability"] == 0.8
        assert payload["voice_settings"]["similarity_boost"] == 0.7


    @pytest.mark.asyncio
    async def test_get_voices_returns_empty_on_http_error(self, client):
        """HTTP failures in get_voices should be swallowed and return []."""
        request = httpx.Request("GET", "https://api.elevenlabs.io/v1/voices")
        response = httpx.Response(500, request=request)
        client.client.get.side_effect = httpx.HTTPStatusError(
            "server error", request=request, response=response
        )

        voices = await client.get_voices()
        assert voices == []

    @pytest.mark.asyncio
    async def test_get_voice_returns_none_on_http_error(self, client):
        client.client.get.side_effect = httpx.TimeoutException("timeout")

        voice = await client.get_voice("voice-xyz")
        assert voice is None

    @pytest.mark.asyncio
    async def test_generate_speech_returns_none_on_http_error(self, client):
        request = httpx.Request("POST", "https://api.elevenlabs.io/v1/text-to-speech/v")
        response = httpx.Response(401, request=request)
        client.client.post.side_effect = httpx.HTTPStatusError(
            "unauthorized", request=request, response=response
        )

        audio = await client.generate_speech("hi", "v")
        assert audio is None

    @pytest.mark.asyncio
    async def test_delete_voice_returns_true_on_success(self, client):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        client.client.delete.return_value = mock_response

        ok = await client.delete_voice("voice-123")
        assert ok is True
        client.client.delete.assert_called_once_with("/v1/voices/voice-123")

    @pytest.mark.asyncio
    async def test_delete_voice_returns_false_on_http_error(self, client):
        request = httpx.Request("DELETE", "https://api.elevenlabs.io/v1/voices/v")
        response = httpx.Response(404, request=request)
        client.client.delete.side_effect = httpx.HTTPStatusError(
            "not found", request=request, response=response
        )

        ok = await client.delete_voice("v")
        assert ok is False

    @pytest.mark.asyncio
    async def test_get_models_returns_empty_on_http_error(self, client):
        client.client.get.side_effect = httpx.ConnectError("no route")
        assert await client.get_models() == []

    @pytest.mark.asyncio
    async def test_get_user_info_returns_none_on_http_error(self, client):
        client.client.get.side_effect = httpx.ConnectError("no route")
        assert await client.get_user_info() is None

    def test_constructor_raises_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key not provided"):
            ElevenLabsClient(api_key=None)


class TestVoiceProfileManager:
    """Test voice profile management."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create test profile manager."""
        return VoiceProfileManager(config_dir=tmp_path)

    def test_create_and_get_profile(self, manager):
        """Test creating and retrieving voice profiles."""
        settings = {"stability": 0.7, "similarity_boost": 0.8}
        manager.create_profile("test-profile", "voice-123", settings)

        profile = manager.get_profile("test-profile")
        assert profile is not None
        assert profile["voice_id"] == "voice-123"
        assert profile["settings"]["stability"] == 0.7

    def test_list_profiles(self, manager):
        """Test listing voice profiles."""
        manager.create_profile("profile1", "voice1", {})
        manager.create_profile("profile2", "voice2", {})

        profiles = manager.list_profiles()
        assert "profile1" in profiles
        assert "profile2" in profiles
        assert len(profiles) == 2

    def test_delete_profile(self, manager):
        """Test deleting voice profiles."""
        manager.create_profile("to-delete", "voice1", {})
        assert "to-delete" in manager.list_profiles()

        manager.delete_profile("to-delete")
        assert "to-delete" not in manager.list_profiles()

    def test_get_nonexistent_profile(self, manager):
        """Test retrieving nonexistent profile."""
        profile = manager.get_profile("nonexistent")
        assert profile is None


if __name__ == "__main__":
    pytest.main([__file__])