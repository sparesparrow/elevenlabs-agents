#!/usr/bin/env python3
"""
ElevenLabs Agents Voice System Demo
===================================

Showcases the voice synthesis capabilities with different personas and engines.
"""

import os
import sys
import time
from elevenlabs_agents import VoiceSystem, VoicePersona, TTSEngine


def print_header():
    """Print demo header"""
    print("🎭 ElevenLabs Agents - Voice System Demo")
    print("=" * 50)
    print()


def check_environment():
    """Check environment and available engines"""
    print("🔍 Checking environment...")

    # Check API key
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if api_key:
        print("✓ ElevenLabs API key found")
    else:
        print("⚠️  ElevenLabs API key not set (ELEVENLABS_API_KEY)")

    print()


def demo_voice_system():
    """Demonstrate voice system capabilities"""
    print("🎤 Initializing voice system...")

    # Initialize with API key if available
    api_key = os.getenv('ELEVENLABS_API_KEY')
    voice_system = VoiceSystem(elevenlabs_api_key=api_key)

    # Show available engines
    engines = voice_system.get_available_engines()
    current_engine = voice_system.get_current_engine()

    print(f"Available engines: {[e.value for e in engines]}")
    print(f"Selected engine: {current_engine.value if current_engine else 'None'}")
    print()

    # Demo messages for different personas
    demo_messages = [
        ("System initialization complete.", VoicePersona.MR_ROBOT, "normal"),
        ("I think we have a problem.", VoicePersona.ELLIOT, "normal"),
        ("The truth is out there.", VoicePersona.FSOCIETY, "high"),
        ("This is a professional announcement.", VoicePersona.PROFESSIONAL, "normal"),
        ("Welcome to our friendly service!", VoicePersona.FRIENDLY, "normal"),
        ("Something mysterious is happening.", VoicePersona.MYSTERIOUS, "low"),
        ("Listen carefully, this is important.", VoicePersona.AUTHORITATIVE, "high"),
        ("This is going to be amazing!", VoicePersona.ENTHUSIASTIC, "high"),
        ("Take a deep breath and relax.", VoicePersona.CALM, "low"),
    ]

    print("🎵 Starting voice demo...")
    print("(Press Ctrl+C to skip)")
    print()

    try:
        for message, persona, urgency in demo_messages:
            print(f"🎤 {persona.value.upper()}: {message}")
            success = voice_system.speak(message, persona, urgency)

            if success:
                print("✓ Success")
            else:
                print("✗ Failed")

            # Small delay between demos
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return False

    print("\n✅ Voice demo completed!")
    return True


def demo_engine_switching():
    """Demonstrate switching between TTS engines"""
    print("\n🔄 Engine Switching Demo")
    print("-" * 30)

    voice_system = VoiceSystem()

    test_message = "Testing engine switching."
    test_persona = VoicePersona.PROFESSIONAL

    # Test each available engine
    for engine in voice_system.get_available_engines():
        print(f"🎤 Testing {engine.value} engine...")

        # Temporarily switch engine
        original_engine = voice_system.voice_engine
        voice_system.voice_engine = engine

        try:
            success = voice_system.speak(test_message, test_persona, "low")
            if success:
                print(f"✓ {engine.value} engine works")
            else:
                print(f"✗ {engine.value} engine failed")
        except Exception as e:
            print(f"✗ {engine.value} engine error: {e}")
        finally:
            # Restore original engine
            voice_system.voice_engine = original_engine

        time.sleep(0.5)


def main():
    """Main demo function"""
    print_header()
    check_environment()

    try:
        success = demo_voice_system()

        if success:
            demo_engine_switching()

        print("\n🎉 Demo completed successfully!")
        print("\nTo run individual tests:")
        print("  python -m elevenlabs_agents.cli --test-voice")
        print("  python -m elevenlabs_agents.cli --list-engines")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()