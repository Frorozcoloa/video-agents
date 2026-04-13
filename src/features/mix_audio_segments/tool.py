"""MCP Tool for the mix audio segments feature."""

from fastmcp import FastMCP
from toon_format import encode
from .models import MixAudioSegmentsInput, AudioSegment
from .logic import mix_audio_segments_logic


def register_mix_audio_segments(mcp: FastMCP):
    @mcp.tool()
    def mix_audio_segments(
        video_path: str,
        segments: list[dict],
        output_path: str | None = None,
        replace_original: bool = False,
    ) -> str:
        """
        Place timed audio clips into a video, mixing or replacing the original audio.

        Each segment defines an audio file and the time range where it plays.
        By default the original video audio is preserved at full volume and
        segments are layered on top. Set replace_original=True to silence the
        original audio and use only the provided segments (equivalent to
        replace_audio behaviour).

        The video stream is copied without re-encoding.

        Args:
            video_path (str): Path to the input video file.
            segments (list[dict]): List of segments, each with:
                - audio_path (str): Path to the audio file.
                - start_ms (int): Start position in milliseconds (>= 0).
                - end_ms (int): End position in milliseconds (> start_ms).
            output_path (str, optional): Output path. Defaults to input with
                                         '_mixed' suffix.
            replace_original (bool): If True, silence the original video audio
                                     and use only the segments. Default False.

        Returns:
            str: Result encoded in TOON format with output_path and segments_count.
        """
        request = MixAudioSegmentsInput(
            video_path=video_path,
            segments=[AudioSegment(**s) for s in segments],
            output_path=output_path,
            replace_original=replace_original,
        )
        result = mix_audio_segments_logic(request)
        return encode(
            {
                "output_path": result.output_path,
                "segments_count": result.segments_count,
            }
        )
