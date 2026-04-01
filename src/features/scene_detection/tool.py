"""MCP Resource for the scene detection feature."""

from fastmcp import FastMCP
from toon_format import encode
from .logic import detect_scenes


def register_scene_detection(mcp: FastMCP):
    @mcp.resource("video://{video_path*}/scenes")
    def scenes_resource(video_path: str) -> str:
        """
        Returns detected scene boundaries for a video file.

        Analyzes the video using PySceneDetect's ContentDetector and returns
        a list of scenes with start/end timestamps in milliseconds.

        Output is in TOON format for LLM token efficiency.
        Note: detection may take several seconds for large video files.

        Args:
            video_path: Absolute path to the video file.

        Returns:
            str: Scene list encoded in TOON format.
        """
        scenes = detect_scenes(video_path)
        scene_dicts = [s.model_dump() for s in scenes]
        return encode({"scenes": scene_dicts})
