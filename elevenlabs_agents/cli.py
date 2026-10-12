"""
Command Line Interface for Voice System Testing
"""

import argparse
import logging
import os
import sys
from typing import Optional

from .voice_system import VoiceSystem, VoicePersona, TTSEngine


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ElevenLabs Agents - Voice Synthesis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test voice system
  elevenlabs-voice-test --test-voice

  # List available engines
  elevenlabs-voice-test --list-engines

  # Speak text with specific persona
  elevenlabs-voice-test --speak "Hello world" --persona mr_robot

  # Test specific engine
  elevenlabs-voice-test --test-engine pyttsx3
        """
    )

    parser.add_argument(
        '--speak', '-s',
        help='Text to speak'
    )

    parser.add_argument(
        '--persona', '-p',
        choices=[p.value for p in VoicePersona],
        default='professional',
        help='Voice persona to use'
    )

    parser.add_argument(
        '--urgency', '-u',
        choices=['low', 'normal', 'high', 'critical'],
        default='normal',
        help='Speech urgency level'
    )

    parser.add_argument(
        '--engine', '-e',
        choices=[e.value for e in TTSEngine],
        help='Specific TTS engine to use'
    )

    parser.add_argument(
        '--test-voice',
        action='store_true',
        help='Test voice system with sample messages'
    )

    parser.add_argument(
        '--list-engines',
        action='store_true',
        help='List available TTS engines'
    )

    parser.add_argument(
        '--test-engine',
        choices=[e.value for e in TTSEngine],
        help='Test specific TTS engine'
    )

    parser.add_argument(
        '--api-key',
        help='ElevenLabs API key (or set ELEVENLABS_API_KEY env var)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Get API key
    api_key = args.api_key or os.getenv('ELEVENLABS_API_KEY')

    # Select TTS engine
    preferred_engine = None
    if args.engine:
        try:
            preferred_engine = TTSEngine(args.engine)
        except ValueError:
            print(f"Invalid TTS engine: {args.engine}")
            print(f"Available engines: {[e.value for e in TTSEngine]}")
            return 1

    # Initialize voice system
    try:
        voice_system = VoiceSystem(
            preferred_engine=preferred_engine,
            elevenlabs_api_key=api_key
        )
    except Exception as e:
        print(f"Failed to initialize voice system: {e}")
        return 1

    # Handle commands
    if args.list_engines:
        engines = voice_system.get_available_engines()
        current = voice_system.get_current_engine()

        print("Available TTS engines:")
        for engine in TTSEngine:
            status = "✓" if engine in engines else "✗"
            current_marker = " (current)" if engine == current else ""
            print(f"  {status} {engine.value}{current_marker}")
        return 0

    if args.test_engine:
        try:
            engine = TTSEngine(args.test_engine)
            print(f"Testing TTS engine: {engine.value}")
            success = voice_system.test_engine(engine)
            if success:
                print("✓ Engine test passed")
                return 0
            else:
                print("✗ Engine test failed")
                return 1
        except ValueError:
            print(f"Invalid TTS engine: {args.test_engine}")
            return 1

    if args.test_voice:
        print("🧪 Testing voice system with all personas...")

        test_messages = [
            ("Hello, I'm Elliot.", VoicePersona.ELLIOT),
            ("I am in control.", VoicePersona.MR_ROBOT),
            ("The truth is out there.", VoicePersona.FSOCIETY),
            ("This is a professional announcement.", VoicePersona.PROFESSIONAL),
        ]

        try:
            for message, persona in test_messages:
                print(f"\n🎤 Testing {persona.value}: {message}")
                success = voice_system.speak(message, persona, "low")
                if not success:
                    print(f"⚠️  Failed to speak with {persona.value}")
        except KeyboardInterrupt:
            print("\nTest interrupted.")
        except Exception as e:
            print(f"Test failed: {e}")
            return 1

        print("\n✓ Voice test complete!")
        return 0

    if args.speak:
        try:
            persona = VoicePersona(args.persona)
            print(f"🎤 Speaking as {persona.value}: {args.speak}")
            success = voice_system.speak(args.speak, persona, args.urgency)
            if success:
                print("✓ Speech completed")
                return 0
            else:
                print("✗ Speech failed")
                return 1
        except ValueError:
            print(f"Invalid persona: {args.persona}")
            return 1
        except Exception as e:
            print(f"Speech failed: {e}")
            return 1

    # No command specified, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())