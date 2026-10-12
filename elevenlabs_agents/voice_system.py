"""
Voice System Module
==================

Main voice synthesis system with multiple TTS engine support.
"""

import subprocess
import sys
import time
import tempfile
import os
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

from .voice_config import VoiceConfig, VoicePersona, TTSEngine, PersonaPreset


class VoiceSystem:
    """
    Advanced voice synthesis system with multiple TTS engines and persona support
    """

    def __init__(self, preferred_engine: Optional[TTSEngine] = None,
                 elevenlabs_api_key: Optional[str] = None):
        self.preferred_engine = preferred_engine
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv('ELEVENLABS_API_KEY')
        self.available_engines = self._detect_available_engines()
        self.voice_engine = self._select_voice_engine()
        self.persona_configs = self._load_persona_configs()
        self.logger = logging.getLogger(__name__)

        # Initialize TTS engines
        self._pyttsx3_engine = None
        self._init_pyttsx3()

        self.logger.info(f"Voice system initialized with engine: {self.voice_engine}")

    def _detect_available_engines(self) -> List[TTSEngine]:
        """Detect all available TTS engines"""
        available = []

        # Check ElevenLabs (requires API key)
        if self.elevenlabs_api_key:
            try:
                import requests
                available.append(TTSEngine.ELEVENLABS)
            except ImportError:
                pass

        # Check pyttsx3 (Python library)
        try:
            import pyttsx3
            available.append(TTSEngine.PYTTSX3)
        except ImportError:
            pass

        # Check espeak-ng
        try:
            subprocess.run(['espeak-ng', '--version'],
                         capture_output=True, check=True, timeout=5)
            available.append(TTSEngine.ESPEAK_NG)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check spd-say
        try:
            subprocess.run(['spd-say', '--version'],
                         capture_output=True, check=True, timeout=5)
            available.append(TTSEngine.SPD_SAY)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check Festival
        try:
            subprocess.run(['festival', '--version'],
                         capture_output=True, check=True, timeout=5)
            available.append(TTSEngine.FESTIVAL)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check gTTS (requires internet)
        try:
            import gtts
            available.append(TTSEngine.GTTS)
        except ImportError:
            pass

        return available

    def _select_voice_engine(self) -> Optional[TTSEngine]:
        """Select the best available voice engine"""
        if self.preferred_engine and self.preferred_engine in self.available_engines:
            return self.preferred_engine

        # Priority order for automatic selection
        priority_order = [
            TTSEngine.ELEVENLABS,    # Best quality, requires API
            TTSEngine.PYTTSX3,       # Cross-platform, good quality
            TTSEngine.ESPEAK_NG,     # High-quality open-source
            TTSEngine.GTTS,          # Good quality, requires internet
            TTSEngine.FESTIVAL,      # Classic TTS
            TTSEngine.SPD_SAY        # Fallback
        ]

        for engine in priority_order:
            if engine in self.available_engines:
                return engine

        if not self.available_engines:
            self.logger.warning("No TTS engines found. Voice synthesis disabled.")
            return None

        # Return first available as last resort
        return self.available_engines[0]

    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        if TTSEngine.PYTTSX3 in self.available_engines:
            try:
                import pyttsx3
                self._pyttsx3_engine = pyttsx3.init()
                # Configure pyttsx3
                voices = self._pyttsx3_engine.getProperty('voices')
                if voices:
                    self._pyttsx3_engine.setProperty('voice', voices[0].id)
            except Exception as e:
                self.logger.error(f"Failed to initialize pyttsx3: {e}")
                self.available_engines.remove(TTSEngine.PYTTSX3)

    def _load_persona_configs(self) -> Dict[VoicePersona, VoiceConfig]:
        """Load persona configurations"""
        configs = {}
        for persona in VoicePersona:
            configs[persona] = PersonaPreset.get_preset(persona)
        return configs

    def speak(self, text: str, persona: VoicePersona = VoicePersona.PROFESSIONAL,
              urgency: str = "normal", **kwargs) -> bool:
        """
        Speak text with specified persona and urgency level

        Args:
            text: Text to speak
            persona: Voice persona to use
            urgency: Urgency level ("low", "normal", "high", "critical")
            **kwargs: Additional parameters for specific TTS engines

        Returns:
            bool: True if speech was successful, False otherwise
        """
        if not self.voice_engine:
            self.logger.warning("No voice engine available. Skipping speech.")
            return False

        config = self.persona_configs[persona]

        # Adjust parameters based on urgency
        urgency_multipliers = {
            "low": 0.8,
            "normal": 1.0,
            "high": 1.2,
            "critical": 1.4
        }

        multiplier = urgency_multipliers.get(urgency, 1.0)
        speed = int(config.speed * multiplier)
        volume = min(100, int(config.volume * multiplier))

        # Format text with persona-specific emphasis
        formatted_text = self._format_text_with_emphasis(text, persona)

        # Add dramatic pause at the end
        pause_duration = config.dramatic_pause * multiplier

        try:
            # Route to appropriate TTS engine
            success = False
            if self.voice_engine == TTSEngine.ELEVENLABS:
                success = self._speak_elevenlabs(formatted_text, config, **kwargs)
            elif self.voice_engine == TTSEngine.PYTTSX3:
                success = self._speak_pyttsx3(formatted_text, config, speed, volume)
            elif self.voice_engine == TTSEngine.ESPEAK_NG:
                success = self._speak_espeak_ng(formatted_text, config, speed, volume, urgency)
            elif self.voice_engine == TTSEngine.SPD_SAY:
                success = self._speak_spd_say(formatted_text, config, speed, volume)
            elif self.voice_engine == TTSEngine.GTTS:
                success = self._speak_gtts(formatted_text, config, speed)
            elif self.voice_engine == TTSEngine.FESTIVAL:
                success = self._speak_festival(formatted_text, config, speed)

            if success:
                # Add dramatic pause after speaking
                time.sleep(pause_duration)
                return True
            else:
                self.logger.error("Speech synthesis failed")
                return False

        except Exception as e:
            self.logger.error(f"Voice synthesis error: {e}")
            return False

    def _speak_elevenlabs(self, text: str, config: VoiceConfig, **kwargs) -> bool:
        """Speak using ElevenLabs API"""
        if not self.elevenlabs_api_key:
            self.logger.error("ElevenLabs API key not provided")
            return False

        try:
            import requests

            url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.elevenlabs_voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }

            data = {
                "text": text,
                "model_id": config.elevenlabs_model,
                "voice_settings": {
                    "stability": config.elevenlabs_stability,
                    "similarity_boost": config.elevenlabs_similarity
                }
            }

            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code == 200:
                # Play the audio
                return self._play_audio_bytes(response.content, 'mp3')
            else:
                self.logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return False

        except ImportError:
            self.logger.error("requests library not available for ElevenLabs")
            return False
        except Exception as e:
            self.logger.error(f"ElevenLabs synthesis failed: {e}")
            return False

    def _speak_pyttsx3(self, text: str, config: VoiceConfig, speed: int, volume: int) -> bool:
        """Speak using pyttsx3"""
        if not self._pyttsx3_engine:
            return False

        try:
            # Configure voice properties
            voices = self._pyttsx3_engine.getProperty('voices')
            if voices:
                # Select voice based on persona
                voice_index = 0
                if config.voice_variant.startswith('f'):
                    # Try to find female voice
                    for i, voice in enumerate(voices):
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            voice_index = i
                            break
                elif config.voice_variant.startswith('m'):
                    # Try to find male voice
                    for i, voice in enumerate(voices):
                        if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                            voice_index = i
                            break

                if voice_index < len(voices):
                    self._pyttsx3_engine.setProperty('voice', voices[voice_index].id)

            self._pyttsx3_engine.setProperty('rate', speed)
            self._pyttsx3_engine.setProperty('volume', volume / 100.0)

            self._pyttsx3_engine.say(text)
            self._pyttsx3_engine.runAndWait()
            return True

        except Exception as e:
            self.logger.error(f"pyttsx3 failed: {e}")
            return False

    def _speak_espeak_ng(self, text: str, config: VoiceConfig, speed: int,
                        volume: int, urgency: str) -> bool:
        """Speak using espeak-ng"""
        formatted_text = self._add_dramatic_effects(text, config.persona)

        cmd = [
            'espeak-ng',
            '-p', str(config.pitch),
            '-s', str(speed),
            '-a', str(volume),
            '-v', f'en+{config.voice_variant}',
            '-g', '10',
            '-m'
        ]

        if urgency in ["high", "critical"]:
            cmd.extend(['-k', '20'])

        cmd.append(formatted_text)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error("espeak-ng timed out")
            return False

    def _speak_spd_say(self, text: str, config: VoiceConfig, speed: int, volume: int) -> bool:
        """Speak using spd-say"""
        cmd = [
            'spd-say',
            '-p', str(config.pitch),
            '-r', str(200 - speed),
            '-i', str(volume),
            '-t', 'male1' if 'm' in config.voice_variant else 'female1',
            text
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error("spd-say timed out")
            return False

    def _speak_gtts(self, text: str, config: VoiceConfig, speed: int) -> bool:
        """Speak using Google Text-to-Speech"""
        try:
            from gtts import gTTS

            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name

            # Generate speech
            tts = gTTS(text=text, lang='en', slow=(speed < 150))
            tts.save(temp_path)

            # Play audio
            return self._play_audio_file(temp_path)

        except ImportError:
            self.logger.error("gTTS or pygame not available")
            return False
        except Exception as e:
            self.logger.error(f"gTTS failed: {e}")
            return False

    def _speak_festival(self, text: str, config: VoiceConfig, speed: int) -> bool:
        """Speak using Festival TTS"""
        festival_script = f"""
(Parameter.set 'Audio_Method 'Audio_Command)
(Parameter.set 'Audio_Command "aplay -q $FILE")
(voice_kal_diphone)
(set! utt1 (Utterance Text "{text}"))
(utt.synth utt1)
(utt.play utt1)
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.scm', delete=False) as temp_file:
            temp_file.write(festival_script)
            temp_path = temp_file.name

        try:
            cmd = ['festival', '-b', temp_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error("Festival timed out")
            return False
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass

    def _play_audio_file(self, file_path: str) -> bool:
        """Play audio file using pygame"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.quit()

            # Clean up
            os.unlink(file_path)
            return True
        except ImportError:
            self.logger.error("pygame not available for audio playback")
            return False
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
            return False

    def _play_audio_bytes(self, audio_bytes: bytes, format: str) -> bool:
        """Play audio bytes using pygame"""
        try:
            import pygame
            import io

            pygame.mixer.init()
            audio_buffer = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_buffer, format)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.quit()
            return True
        except ImportError:
            self.logger.error("pygame not available for audio playback")
            return False
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
            return False

    def _format_text_with_emphasis(self, text: str, persona: VoicePersona) -> str:
        """Add persona-specific text formatting"""
        if persona == VoicePersona.ELLIOT:
            # Elliot: hesitant, uses "um", "uh", pauses
            return text.replace(".", "...").replace("!", "!...").replace("?", "?...")
        elif persona == VoicePersona.MR_ROBOT:
            # Mr. Robot: direct, commanding, emphatic
            return text.replace(".", ".").replace("!", "!!").replace("?", "!")
        elif persona == VoicePersona.FSOCIETY:
            # fsociety: cryptic, rebellious, dramatic
            return text.replace(".", "...").replace("!", "!").replace("?", "?")

        return text

    def _add_dramatic_effects(self, text: str, persona: VoicePersona) -> str:
        """Add SSML-like tags for dramatic effects (espeak-ng only)"""
        if self.voice_engine == TTSEngine.ESPEAK_NG:
            if persona == VoicePersona.ELLIOT:
                text = f'<voice name="en-us">{text}</voice>'
                text = text.replace('breach', '<emphasis level="strong">breach</emphasis>')
                text = text.replace('intrusion', '<emphasis level="strong">intrusion</emphasis>')
            elif persona == VoicePersona.MR_ROBOT:
                text = f'<voice name="en-gb">{text}</voice>'
                text = text.replace('control', '<emphasis level="strong">control</emphasis>')
                text = text.replace('system', '<emphasis level="strong">system</emphasis>')
            elif persona == VoicePersona.FSOCIETY:
                text = f'<voice name="en">{text}</voice>'
                text = text.replace('hack', '<emphasis level="strong">hack</emphasis>')
                text = text.replace('truth', '<emphasis level="strong">truth</emphasis>')

        return text

    def get_available_engines(self) -> List[TTSEngine]:
        """Get list of available TTS engines"""
        return self.available_engines.copy()

    def get_current_engine(self) -> Optional[TTSEngine]:
        """Get currently selected TTS engine"""
        return self.voice_engine

    def set_persona_config(self, persona: VoicePersona, config: VoiceConfig):
        """Update configuration for a specific persona"""
        self.persona_configs[persona] = config

    def test_engine(self, engine: TTSEngine) -> bool:
        """Test if a specific TTS engine works"""
        if engine not in self.available_engines:
            return False

        old_engine = self.voice_engine
        self.voice_engine = engine

        try:
            success = self.speak("Test message", VoicePersona.PROFESSIONAL, "low")
            return success
        finally:
            self.voice_engine = old_engine