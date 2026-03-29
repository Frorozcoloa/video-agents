"""Tool for the audio transcription feature."""

from fastmcp import FastMCP
from .logic import transcribe_audio_logic


def register_audio_transcription(mcp: FastMCP):
    """
    Register the audio transcription tool with the MCP server.

    Args:
        mcp: The MCP server instance.
    """

    @mcp.tool()
    def transcribe_audio(
        audio_path: str,
        model_size: str = "base",
    ) -> str:
        """
        Transcribes an audio file and returns text with millisecond timestamps.

        The output is returned in TOON (Token-Oriented Object Notation) format, a compact
        and spec-compliant structure optimized for LLM token efficiency.

        Args:
            audio_path (str): The path to the audio file (e.g., .mp3, .wav).
            model_size (str): Whisper model size (default: base). Use 'small' or 'medium' for more accuracy.
            progress (Any, optional): Progress reporting (ignored in sync mode).

        Returns:
            str: Transcription data encoded in TOON format.
        """
        return transcribe_audio_logic(audio_path=audio_path, model_size=model_size)
