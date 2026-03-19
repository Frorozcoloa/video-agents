"""Tool for the audio transcription feature."""

from fastmcp import FastMCP
from .logic import transcribe_audio_logic
from .models import TranscriptionResponse, TranscriptionSegment


def register_audio_transcription(mcp: FastMCP):
    """
    Register the audio transcription tool with the MCP server.

    Args:
        mcp: The MCP server instance.
    """

    @mcp.tool()
    def transcribe_audio(
        audio_path: str, model_size: str = "base"
    ) -> TranscriptionResponse:
        """
        Transcribes an audio file and returns text with millisecond timestamps.

        Args:
            audio_path (str): The path to the audio file (e.g., .mp3, .wav).
            model_size (str): Whisper model size (default: base). Use 'small' or 'medium' for more accuracy.

        Returns:
            TranscriptionResponse: A list of objects with text, start time, and end time in ms.
        """
        results = transcribe_audio_logic(audio_path=audio_path, model_size=model_size)
        segments = [TranscriptionSegment(**res) for res in results]
        return TranscriptionResponse(segments=segments)
