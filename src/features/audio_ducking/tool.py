"""MCP Tool for the audio ducking feature."""

from fastmcp import FastMCP
from toon_format import encode
from .models import AudioDuckingInput
from .logic import duck_audio


def register_audio_ducking(mcp: FastMCP):
    @mcp.tool()
    def audio_ducking(
        voice_path: str,
        music_path: str,
        output_path: str,
        threshold: float = 0.1,
        ratio: float = 5.0,
        attack: int = 20,
        release: int = 500,
    ) -> str:
        """
        Mix a voice track over background music with automatic sidechain ducking.

        The music volume is automatically reduced whenever the voice is active,
        using FFmpeg's sidechaincompress filter. The voice track is split via
        asplit so it acts as both the sidechain trigger and a passthrough stream.
        Both inputs are normalised to stereo before processing.

        Args:
            voice_path (str): Path to the voice/voiceover audio file.
            music_path (str): Path to the background music audio file.
            output_path (str): Path for the mixed output audio file.
            threshold (float): Compression threshold 0.0–1.0 (default 0.1).
            ratio (float): Compression ratio ≥1.0 (default 5.0).
            attack (int): Attack time in ms ≥1 (default 20).
            release (int): Release time in ms ≥1 (default 500).

        Returns:
            str: Result encoded in TOON format with output_path and applied params.
        """
        request = AudioDuckingInput(
            voice_path=voice_path,
            music_path=music_path,
            output_path=output_path,
            threshold=threshold,
            ratio=ratio,
            attack=attack,
            release=release,
        )
        result = duck_audio(request)
        return encode(
            {
                "output_path": result.output_path,
                "params": result.params.model_dump(),
            }
        )
