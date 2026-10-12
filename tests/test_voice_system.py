"""
Tests for Voice System Module
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from elevenlabs_agents import VoiceSystem, VoicePersona, TTSEngine, VoiceConfig


class TestVoiceSystem(unittest.TestCase):
    """Test cases for VoiceSystem class"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv('ELEVENLABS_API_KEY', 'test_key')

    def test_initialization(self):
        """Test voice system initialization"""
        voice_system = VoiceSystem(elevenlabs_api_key=self.api_key)
        self.assertIsInstance(voice_system, VoiceSystem)
        self.assertIsNotNone(voice_system.available_engines)

    def test_persona_configs_loaded(self):
        """Test that persona configurations are loaded"""
        voice_system = VoiceSystem()
        self.assertIn(VoicePersona.ELLIOT, voice_system.persona_configs)
        self.assertIn(VoicePersona.MR_ROBOT, voice_system.persona_configs)
        self.assertIn(VoicePersona.PROFESSIONAL, voice_system.persona_configs)

    @patch('elevenlabs_agents.voice_system.VoiceSystem._speak_pyttsx3')
    def test_speak_with_pyttsx3(self, mock_speak):
        """Test speaking with pyttsx3 engine"""
        mock_speak.return_value = True

        with patch('elevenlabs_agents.voice_system.VoiceSystem._detect_available_engines',
                   return_value=[TTSEngine.PYTTSX3]):
            voice_system = VoiceSystem()
            result = voice_system.speak("Test message", VoicePersona.PROFESSIONAL)
            self.assertTrue(result)
            mock_speak.assert_called_once()

    @patch('subprocess.run')
    def test_speak_with_espeak_ng(self, mock_subprocess):
        """Test speaking with espeak-ng engine"""
        mock_subprocess.return_value = MagicMock(returncode=0)

        with patch('elevenlabs_agents.voice_system.VoiceSystem._detect_available_engines',
                   return_value=[TTSEngine.ESPEAK_NG]):
            voice_system = VoiceSystem()
            result = voice_system.speak("Test message", VoicePersona.ELLIOT)
            self.assertTrue(result)

    def test_engine_selection(self):
        """Test TTS engine selection logic"""
        # Test preferred engine selection
        voice_system = VoiceSystem(preferred_engine=TTSEngine.PYTTSX3)

        with patch.object(voice_system, '_detect_available_engines',
                         return_value=[TTSEngine.PYTTSX3, TTSEngine.ESPEAK_NG]):
            selected = voice_system._select_voice_engine()
            self.assertEqual(selected, TTSEngine.PYTTSX3)

    def test_urgency_multipliers(self):
        """Test urgency level adjustments"""
        voice_system = VoiceSystem()

        # Test different urgency levels
        test_cases = [
            ("low", 0.8),
            ("normal", 1.0),
            ("high", 1.2),
            ("critical", 1.4),
        ]

        for urgency, expected_multiplier in test_cases:
            with self.subTest(urgency=urgency):
                config = voice_system.persona_configs[VoicePersona.PROFESSIONAL]
                multiplier = voice_system._urgency_multipliers.get(urgency, 1.0)
                self.assertEqual(multiplier, expected_multiplier)

    def test_text_formatting(self):
        """Test persona-specific text formatting"""
        voice_system = VoiceSystem()

        # Test Elliot formatting (hesitant)
        elliot_text = voice_system._format_text_with_emphasis("Hello!", VoicePersona.ELLIOT)
        self.assertIn("...", elliot_text)

        # Test Mr. Robot formatting (commanding)
        mr_robot_text = voice_system._format_text_with_emphasis("Hello!", VoicePersona.MR_ROBOT)
        self.assertIn("!!", mr_robot_text)

    def test_voice_config_validation(self):
        """Test VoiceConfig validation"""
        # Valid config
        config = VoiceConfig(
            persona=VoicePersona.PROFESSIONAL,
            pitch=50,
            speed=150,
            volume=80
        )
        self.assertEqual(config.pitch, 50)

        # Invalid pitch
        with self.assertRaises(ValueError):
            VoiceConfig(
                persona=VoicePersona.PROFESSIONAL,
                pitch=150  # Invalid: > 100
            )

        # Invalid speed
        with self.assertRaises(ValueError):
            VoiceConfig(
                persona=VoicePersona.PROFESSIONAL,
                speed=400  # Invalid: > 300
            )


class TestVoiceConfig(unittest.TestCase):
    """Test cases for VoiceConfig class"""

    def test_config_creation(self):
        """Test VoiceConfig creation"""
        config = VoiceConfig(
            persona=VoicePersona.ELLIOT,
            pitch=45,
            speed=130,
            volume=75,
            voice_variant="male_uncertain",
            dramatic_pause=0.8
        )

        self.assertEqual(config.persona, VoicePersona.ELLIOT)
        self.assertEqual(config.pitch, 45)
        self.assertEqual(config.speed, 130)
        self.assertEqual(config.volume, 75)

    def test_elevenlabs_config(self):
        """Test ElevenLabs specific configuration"""
        config = VoiceConfig(
            persona=VoicePersona.PROFESSIONAL,
            elevenlabs_voice_id="test_voice_id",
            elevenlabs_model="eleven_monolingual_v1",
            elevenlabs_stability=0.7,
            elevenlabs_similarity=0.8
        )

        self.assertEqual(config.elevenlabs_voice_id, "test_voice_id")
        self.assertEqual(config.elevenlabs_stability, 0.7)
        self.assertEqual(config.elevenlabs_similarity, 0.8)


class TestPersonaPresets(unittest.TestCase):
    """Test cases for persona presets"""

    def test_elliot_preset(self):
        """Test Elliot persona preset"""
        from elevenlabs_agents.voice_config import PersonaPreset

        config = PersonaPreset.get_elliot()
        self.assertEqual(config.persona, VoicePersona.ELLIOT)
        self.assertEqual(config.pitch, 45)
        self.assertEqual(config.speed, 130)
        self.assertLess(config.dramatic_pause, 1.0)  # Longer pause

    def test_mr_robot_preset(self):
        """Test Mr. Robot persona preset"""
        from elevenlabs_agents.voice_config import PersonaPreset

        config = PersonaPreset.get_mr_robot()
        self.assertEqual(config.persona, VoicePersona.MR_ROBOT)
        self.assertGreater(config.pitch, 50)  # Higher pitch
        self.assertGreater(config.speed, 140)  # Faster speed
        self.assertLess(config.dramatic_pause, 0.5)  # Shorter pause

    def test_fsociety_preset(self):
        """Test fsociety persona preset"""
        from elevenlabs_agents.voice_config import PersonaPreset

        config = PersonaPreset.get_fsociety()
        self.assertEqual(config.persona, VoicePersona.FSOCIETY)
        self.assertTrue(config.voice_variant.startswith('f'))  # Female variant

    def test_get_preset_method(self):
        """Test get_preset method for all personas"""
        from elevenlabs_agents.voice_config import PersonaPreset

        for persona in VoicePersona:
            config = PersonaPreset.get_preset(persona)
            self.assertEqual(config.persona, persona)
            self.assertIsInstance(config, VoiceConfig)


if __name__ == '__main__':
    unittest.main()