"""
Voice Configuration Module
=========================

Configuration classes for voice synthesis settings and personas.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class VoicePersona(Enum):
    """Voice personas for different characters and personalities"""

    # Mr. Robot inspired personas
    ELLIOT = "elliot"          # Hesitant, anxious, precise
    MR_ROBOT = "mr_robot"      # Commanding, intense, urgent
    FSOCIETY = "fsociety"      # Rebellious, cryptic, dramatic

    # Professional personas
    PROFESSIONAL = "professional"    # Clear, confident, neutral
    FRIENDLY = "friendly"           # Warm, approachable, engaging

    # Character personas
    MYSTERIOUS = "mysterious"       # Enigmatic, intriguing, suspenseful
    AUTHORITATIVE = "authoritative" # Firm, commanding, decisive

    # Emotional personas
    ENTHUSIASTIC = "enthusiastic"   # Energetic, excited, passionate
    CALM = "calm"                  # Soothing, relaxed, composed


class TTSEngine(Enum):
    """Available TTS engines in order of preference"""

    ELEVENLABS = "elevenlabs"   # Primary: ElevenLabs API
    PYTTSX3 = "pyttsx3"        # Cross-platform Python TTS
    ESPEAK_NG = "espeak-ng"    # High-quality open-source TTS
    GTTS = "gtts"             # Google Text-to-Speech (requires internet)
    FESTIVAL = "festival"      # Classic TTS engine
    SPD_SAY = "spd-say"        # Speech dispatcher fallback


@dataclass
class VoiceConfig:
    """Configuration for voice synthesis parameters"""

    persona: VoicePersona
    pitch: int = 50           # Voice pitch (0-100)
    speed: int = 150          # Speech speed (words per minute)
    volume: int = 80          # Volume level (0-100)
    voice_variant: str = ""   # Engine-specific voice variant
    dramatic_pause: float = 0.5  # Pause duration after speech

    # ElevenLabs specific settings
    elevenlabs_voice_id: Optional[str] = None
    elevenlabs_model: str = "eleven_monolingual_v1"
    elevenlabs_stability: float = 0.5
    elevenlabs_similarity: float = 0.8

    def __post_init__(self):
        """Validate configuration values"""
        if not (0 <= self.pitch <= 100):
            raise ValueError("Pitch must be between 0 and 100")
        if not (50 <= self.speed <= 300):
            raise ValueError("Speed must be between 50 and 300 WPM")
        if not (0 <= self.volume <= 100):
            raise ValueError("Volume must be between 0 and 100")
        if not (0 <= self.dramatic_pause <= 5):
            raise ValueError("Dramatic pause must be between 0 and 5 seconds")


class PersonaPreset:
    """Predefined persona configurations"""

    @staticmethod
    def get_elliot() -> VoiceConfig:
        """Elliot Alderson - hesitant, anxious, precise"""
        return VoiceConfig(
            persona=VoicePersona.ELLIOT,
            pitch=45,      # Lower pitch, uncertain
            speed=130,     # Slightly slower, thoughtful
            volume=75,
            voice_variant="male_uncertain",
            dramatic_pause=0.8,
            elevenlabs_voice_id="29vD33N1CtxCmqQRPOHJ",  # Example voice ID
            elevenlabs_stability=0.3,
            elevenlabs_similarity=0.7
        )

    @staticmethod
    def get_mr_robot() -> VoiceConfig:
        """Mr. Robot - commanding, intense, urgent"""
        return VoiceConfig(
            persona=VoicePersona.MR_ROBOT,
            pitch=65,      # Higher pitch, intense
            speed=160,     # Faster, urgent
            volume=90,
            voice_variant="male_commanding",
            dramatic_pause=0.3,
            elevenlabs_voice_id="21m00Tcm4TlvDq8ikWAM",  # Example voice ID
            elevenlabs_stability=0.8,
            elevenlabs_similarity=0.9
        )

    @staticmethod
    def get_fsociety() -> VoiceConfig:
        """fsociety - rebellious, cryptic, dramatic"""
        return VoiceConfig(
            persona=VoicePersona.FSOCIETY,
            pitch=55,      # Medium pitch, mysterious
            speed=145,     # Moderate speed, deliberate
            volume=85,
            voice_variant="female_rebellious",
            dramatic_pause=0.6,
            elevenlabs_voice_id="AZnzlk1XvdvUeBnXmlld",  # Example voice ID
            elevenlabs_stability=0.6,
            elevenlabs_similarity=0.8
        )

    @staticmethod
    def get_professional() -> VoiceConfig:
        """Professional - clear, confident, neutral"""
        return VoiceConfig(
            persona=VoicePersona.PROFESSIONAL,
            pitch=50,      # Neutral pitch
            speed=150,     # Standard speed
            volume=80,
            voice_variant="neutral_professional",
            dramatic_pause=0.4,
            elevenlabs_voice_id="pNInz6obpgDQGcFmaJgB",  # Example voice ID
            elevenlabs_stability=0.7,
            elevenlabs_similarity=0.8
        )

    @staticmethod
    def get_preset(persona: VoicePersona) -> VoiceConfig:
        """Get preset configuration for a persona"""
        presets = {
            VoicePersona.ELLIOT: PersonaPreset.get_elliot,
            VoicePersona.MR_ROBOT: PersonaPreset.get_mr_robot,
            VoicePersona.FSOCIETY: PersonaPreset.get_fsociety,
            VoicePersona.PROFESSIONAL: PersonaPreset.get_professional,
        }

        preset_func = presets.get(persona)
        if preset_func:
            return preset_func()

        # Default configuration for unknown personas
        return VoiceConfig(
            persona=persona,
            pitch=50,
            speed=150,
            volume=80,
            voice_variant="default",
            dramatic_pause=0.5
        )