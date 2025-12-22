"""
ElevenLabs API client for voice synthesis and cloning.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Client for ElevenLabs Text-to-Speech API."""

    BASE_URL = "https://api.elevenlabs.io"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key not provided")

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            },
            timeout=30.0
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def get_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        try:
            response = await self.client.get("/v1/voices")
            response.raise_for_status()
            data = response.json()
            return data.get("voices", [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to get voices: {e}")
            return []

    async def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific voice."""
        try:
            response = await self.client.get(f"/v1/voices/{voice_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get voice {voice_id}: {e}")
            return None

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_monolingual_v1",
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[bytes]:
        """Generate speech from text."""
        try:
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": voice_settings or {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }

            response = await self.client.post(
                f"/v1/text-to-speech/{voice_id}",
                json=payload,
                headers={"Accept": "audio/mpeg"}
            )
            response.raise_for_status()
            return response.content

        except httpx.HTTPError as e:
            logger.error(f"Failed to generate speech: {e}")
            return None

    async def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        try:
            response = await self.client.get("/v1/models")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get models: {e}")
            return []

    async def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user account information."""
        try:
            response = await self.client.get("/v1/user")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user info: {e}")
            return None


class VoiceProfileManager:
    """Manages voice profiles and preferences."""

    def __init__(self, config_dir: Path = Path.home() / ".elevenlabs-mia"):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.profiles_file = self.config_dir / "voice_profiles.json"
        self._load_profiles()

    def _load_profiles(self):
        """Load voice profiles from disk."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    self.profiles = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load voice profiles: {e}")
                self.profiles = {}
        else:
            self.profiles = {}

    def _save_profiles(self):
        """Save voice profiles to disk."""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save voice profiles: {e}")

    def create_profile(self, name: str, voice_id: str, settings: Dict[str, Any]):
        """Create a voice profile."""
        self.profiles[name] = {
            "voice_id": voice_id,
            "settings": settings,
            "created_at": asyncio.get_event_loop().time()
        }
        self._save_profiles()

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a voice profile."""
        return self.profiles.get(name)

    def list_profiles(self) -> List[str]:
        """List all voice profile names."""
        return list(self.profiles.keys())

    def delete_profile(self, name: str):
        """Delete a voice profile."""
        if name in self.profiles:
            del self.profiles[name]
            self._save_profiles()