"""
FastMCP server for video agents.
"""

from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world
from features.audio_extraction.tool import register_audio_extraction
from features.audio_transcription.tool import register_audio_transcription
from features.video_clipping.tool import register_video_clipping
from features.scene_detection.tool import register_scene_detection
from features.broll_overlay.tool import register_broll_overlay

# Initialize FastMCP server
mcp = FastMCP("Video Agents")

# Register features
register_hello_world(mcp)
register_audio_extraction(mcp)
register_audio_transcription(mcp)
register_video_clipping(mcp)
register_scene_detection(mcp)
register_broll_overlay(mcp)

if __name__ == "__main__":
    print("Starting MCP server on http://localhost:8000")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
