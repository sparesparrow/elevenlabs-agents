"""
ElevenLabs Agents - Voice integration for MIA IoT control system
"""

def main():
    """Main entry point for the ElevenLabs MCP server."""
    import asyncio
    import sys
    import argparse
    from pathlib import Path

    # Add the src directory to Python path
    src_path = Path(__file__).parent
    sys.path.insert(0, str(src_path))

    from .mcp_server import serve

    parser = argparse.ArgumentParser(description="ElevenLabs MCP Server for MIA")
    parser.add_argument(
        "--elevenlabs-api-key",
        help="ElevenLabs API key (can also set ELEVENLABS_API_KEY env var)"
    )
    parser.add_argument(
        "--mia-host",
        default="localhost",
        help="MIA FastAPI server host (default: localhost)"
    )
    parser.add_argument(
        "--mia-port",
        type=int,
        default=8000,
        help="MIA FastAPI server port (default: 8000)"
    )

    args = parser.parse_args()

    try:
        asyncio.run(serve(
            elevenlabs_api_key=args.elevenlabs_api_key,
            mia_host=args.mia_host,
            mia_port=args.mia_port
        ))
    except KeyboardInterrupt:
        print("\nShutting down ElevenLabs MCP server...")
    except Exception as e:
        print(f"Error running ElevenLabs MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()