"""
FastMCP server for video agents.
"""

from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world
from features.audio_extraction.tool import register_audio_extraction
from features.audio_transcription.tool import register_audio_transcription
from features.video_clipping.tool import register_video_clipping

# Initialize FastMCP server
mcp = FastMCP("Video Agents")

# Register features
register_hello_world(mcp)
register_audio_extraction(mcp)
register_audio_transcription(mcp)
register_video_clipping(mcp)

if __name__ == "__main__":
    print("Starting MCP server on http://localhost:8000")
    mcp.run(transport="http")
