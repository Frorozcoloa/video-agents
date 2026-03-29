"""Tool for the video clipping feature."""

from fastmcp import FastMCP
from typing import Literal
from .models import ClippingRequest, JumpCutRequest
from .logic import clip_video_logic, process_jump_cut


def register_video_clipping(mcp: FastMCP):
    @mcp.tool()
    def clip_video(
        video_path: str,
        start_time: int,
        end_time: int,
        output_path: str | None = None,
        mode: Literal["fast", "exact"] = "fast",
    ) -> str:
        """
        Clips a segment from a video file.

        Args:
            video_path (str): The path to the input video file.
            start_time (int): Start timestamp in milliseconds (e.g., 10500 for 10.5s).
            end_time (int): End timestamp in milliseconds (e.g., 20000 for 20.0s).
            output_path (str, optional): The desired output path for the clipped video.
            mode (Literal["fast", "exact"]): 'fast' for streamcopy (speed, keyframe-accurate),
                                             'exact' for re-encoding (frame-accurate).
            str: The path to the clipped video file.
        """
        request = ClippingRequest(
            video_path=video_path,
            start_time=start_time,
            end_time=end_time,
            output_video_path=output_path,
            mode=mode,
        )
        response = clip_video_logic(request)
        return response.video_path

    @mcp.tool()
    def jump_cut_video(
        video_path: str,
        audio_path: str,
        output_path: str | None = None,
    ) -> str:
        """
        Creates a jump cut video by automatically detecting and removing silences using VAD.

        Args:
            video_path (str): The path to the input video file.
            audio_path (str): The path to the extracted audio file to use for silence detection.
            output_path (str, optional): The desired output path.

        Returns:
            str: The path to the jump cut video file.
        """
        request = JumpCutRequest(
            video_path=video_path,
            audio_path=audio_path,
            output_video_path=output_path,
        )
        response = process_jump_cut(request)
        return response.video_path
