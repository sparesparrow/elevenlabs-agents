#!/bin/bash
# ElevenLabs Agents Voice Module Setup Script
# Installs dependencies and sets up the voice synthesis module

set -e

echo "🎭 Setting up ElevenLabs Agents Voice Module..."
echo "==============================================="

# Check if running on supported OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✓ Linux detected"

    # Update package lists
    echo "📦 Updating package lists..."
    sudo apt-get update

    # Install espeak-ng (high-quality TTS)
    echo "🎤 Installing espeak-ng TTS engine..."
    if ! command -v espeak-ng &> /dev/null; then
        sudo apt-get install -y espeak-ng espeak-ng-data
        echo "✓ espeak-ng installed"
    else
        echo "✓ espeak-ng already installed"
    fi

    # Install Festival TTS
    echo "🎤 Installing Festival TTS engine..."
    if ! command -v festival &> /dev/null; then
        sudo apt-get install -y festival festvox-kallpc16k
        echo "✓ Festival installed"
    else
        echo "✓ Festival already installed"
    fi

    # Install speech-dispatcher (fallback)
    echo "🎤 Installing speech-dispatcher..."
    if ! command -v spd-say &> /dev/null; then
        sudo apt-get install -y speech-dispatcher
        echo "✓ speech-dispatcher installed"
    else
        echo "✓ speech-dispatcher already installed"
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected"

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi

    # Install espeak-ng
    echo "🎤 Installing espeak-ng..."
    if ! command -v espeak-ng &> /dev/null; then
        brew install espeak-ng
        echo "✓ espeak-ng installed"
    else
        echo "✓ espeak-ng already installed"
    fi

else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "This script supports Linux and macOS only."
    exit 1
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user -e ".[tts]" 2>/dev/null || echo "⚠️  Some Python packages may require manual installation"

# Install optional TTS engines
echo "🎵 Installing optional TTS engines..."
pip3 install --user pyttsx3 gtts pygame 2>/dev/null || echo "⚠️  Some optional packages may require manual installation"

# Install the package in development mode
echo "📦 Installing elevenlabs-agents package..."
pip3 install -e . 2>/dev/null || echo "⚠️  Package installation may require manual setup"

# Make scripts executable
chmod +x demo.py

# Test the installation
echo "🧪 Testing installation..."
if python3 -c "from elevenlabs_agents import VoiceSystem; print('✓ Import successful')"; then
    echo "✓ Basic import test passed"
else
    echo "✗ Import test failed"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo "=================="
echo ""
echo "Usage:"
echo "  # Run demo"
echo "  python3 demo.py"
echo ""
echo "  # Test voice system"
echo "  elevenlabs-voice-test --test-voice"
echo ""
echo "  # List available engines"
echo "  elevenlabs-voice-test --list-engines"
echo ""
echo "  # Speak with specific persona"
echo "  elevenlabs-voice-test --speak \"Hello world\" --persona mr_robot"
echo ""
echo "Environment Setup:"
echo "  # Set ElevenLabs API key (optional, for premium voices)"
echo "  export ELEVENLABS_API_KEY=\"your_api_key_here\""
echo ""
echo "Available TTS engines:"
if command -v espeak-ng &> /dev/null; then
    echo "  ✓ espeak-ng (high quality, offline)"
fi
if python3 -c "import pyttsx3" 2>/dev/null; then
    echo "  ✓ pyttsx3 (cross-platform, offline)"
fi
if python3 -c "import gtts" 2>/dev/null; then
    echo "  ✓ Google TTS (web-based, requires internet)"
fi
if command -v festival &> /dev/null; then
    echo "  ✓ Festival (classic TTS, offline)"
fi
if command -v spd-say &> /dev/null; then
    echo "  ✓ spd-say (accessibility, offline)"
fi
echo ""
echo "Happy synthesizing! 🎤🤖"