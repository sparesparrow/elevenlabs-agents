"""
ElevenLabs Agents - Voice Synthesis Module
==========================================

A comprehensive voice synthesis library with multiple TTS engines and persona support.

Features:
- ElevenLabs API integration for high-quality voice synthesis
- Multiple fallback TTS engines (pyttsx3, espeak-ng, gTTS, etc.)
- Voice personas inspired by characters and personalities
- Dramatic speech effects and emphasis
- Cross-platform support

Example:
    >>> from elevenlabs_agents import VoiceSystem, VoicePersona
    >>> voice = VoiceSystem()
    >>> voice.speak("Hello world", VoicePersona.ELLIOT)
"""

__version__ = "0.1.0"
__author__ = "Enhanced by AI Assistant"
__description__ = "Voice synthesis module for ElevenLabs agents"

from .voice_system import VoiceSystem, VoicePersona, TTSEngine
from .voice_config import VoiceConfig

__all__ = [
    "VoiceSystem",
    "VoicePersona",
    "TTSEngine",
    "VoiceConfig"
]