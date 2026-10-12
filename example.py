#!/usr/bin/env python3
"""
Simple example of using the ElevenLabs Agents voice system
"""

from elevenlabs_agents import VoiceSystem, VoicePersona, TTSEngine

def main():
    """Simple voice synthesis example"""

    # Initialize voice system (will auto-detect available engines)
    print("🎤 Initializing voice system...")
    voice = VoiceSystem()

    # Show current engine
    current_engine = voice.get_current_engine()
    print(f"Using TTS engine: {current_engine.value if current_engine else 'None'}")

    # Basic speech
    print("\n🎵 Speaking with default professional voice...")
    voice.speak("Hello, this is a professional announcement.")

    # Different personas
    print("\n🎭 Speaking with Elliot persona...")
    voice.speak("I think we have a problem.", VoicePersona.ELLIOT)

    print("\n🎭 Speaking with Mr. Robot persona...")
    voice.speak("I am in control.", VoicePersona.MR_ROBOT)

    print("\n🎭 Speaking with fsociety persona...")
    voice.speak("The truth is out there.", VoicePersona.FSOCIETY)

    # Different urgency levels
    print("\n🚨 Speaking with high urgency...")
    voice.speak("Critical system alert!", VoicePersona.MR_ROBOT, "critical")

    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()