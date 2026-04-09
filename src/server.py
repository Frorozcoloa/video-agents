"""
FastMCP server for video agents.
"""

import logging

from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world
from features.audio_extraction.tool import register_audio_extraction
from features.audio_transcription.tool import register_audio_transcription
from features.video_clipping.tool import register_video_clipping
from features.scene_detection.tool import register_scene_detection
from features.broll_overlay.tool import register_broll_overlay
from features.audio_ducking.tool import register_audio_ducking
from features.mix_audio_segments.tool import register_mix_audio_segments

HOST = "0.0.0.0"
PORT = 8000
TRANSPORT = "http"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Video Agents")

# Register features
register_hello_world(mcp)
register_audio_extraction(mcp)
register_audio_transcription(mcp)
register_video_clipping(mcp)
register_scene_detection(mcp)
register_broll_overlay(mcp)
register_audio_ducking(mcp)
register_mix_audio_segments(mcp)


def main() -> None:
    """Run the MCP server."""
    logger.info("Transport : %s", TRANSPORT)
    logger.info("Host      : %s", HOST)
    logger.info("Port      : %d", PORT)
    logger.info("Endpoint  : http://%s:%d/mcp", HOST, PORT)
    mcp.run(transport=TRANSPORT, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
