"""Tool for the audio extraction feature."""

from fastmcp import FastMCP
from .models import ExtractionRequest
from .logic import extract_audio_logic


def register_audio_extraction(mcp: FastMCP):
    @mcp.tool()
    def extract_audio(video_path: str, output_path: str | None = None) -> str:
        """
        Extracts high-quality audio from a video file.

        Args:
            video_path (str): The path to the input video file.
            output_path (str, optional): The desired output path for the audio.
            progress (Any, optional): Progress reporting (ignored in sync mode).

        Returns:
            str: The path to the extracted audio file.
        """
        request = ExtractionRequest(
            video_path=video_path, output_audio_path=output_path
        )
        response = extract_audio_logic(request)
        return response.audio_path
