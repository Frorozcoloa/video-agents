"""MCP Tool for the B-roll overlay feature."""

from fastmcp import FastMCP
from toon_format import encode
from .models import BrollRequest
from .logic import apply_broll as apply_broll_logic


def register_broll_overlay(mcp: FastMCP):
    @mcp.tool()
    def apply_broll(
        video_path: str,
        broll_path: str,
        start_ms: int,
        end_ms: int,
        output_path: str | None = None,
    ) -> str:
        """
        Overlays a B-roll clip onto a time-bounded segment of the main video.

        Uses FFmpeg's overlay filter with eof_action=repeat to freeze the last
        B-roll frame when the B-roll is shorter than the target segment.
        The B-roll is scaled to match the main video's dimensions. Main audio
        is preserved; B-roll audio is discarded.

        Args:
            video_path (str): Path to the main video file.
            broll_path (str): Path to the B-roll clip.
            start_ms (int): Overlay start timestamp in milliseconds.
            end_ms (int): Overlay end timestamp in milliseconds.
            output_path (str, optional): Output path. Defaults to input path
                                         with _broll suffix.

        Returns:
            str: Result encoded in TOON format containing the output path.
        """
        request = BrollRequest(
            video_path=video_path,
            broll_path=broll_path,
            start_ms=start_ms,
            end_ms=end_ms,
            output_path=output_path,
        )
        result_path = apply_broll_logic(request)
        return encode({"output_path": result_path})
