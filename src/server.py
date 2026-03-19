"""
FastMCP server for video agents.
"""
from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world
from features.audio_extraction.tool import register_audio_extraction
from features.audio_transcription.tool import register_audio_transcription

# Initialize FastMCP server
mcp = FastMCP("Video Agents")

# Register features
register_hello_world(mcp)
register_audio_extraction(mcp)
register_audio_transcription(mcp)

if __name__ == "__main__":
    print("Starting MCP server on http://localhost:8000")
    mcp.run(transport="http")
