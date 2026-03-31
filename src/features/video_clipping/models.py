"""Models for the video clipping feature."""

from pydantic import BaseModel, Field
from typing import Literal


class ClippingRequest(BaseModel):
    """
    Request model for the video clipping feature.

    video_path: Path to the input video file.
    start_time: Start timestamp in milliseconds (e.g., 10500 for 10.5s).
    end_time: End timestamp in milliseconds (e.g., 20000 for 20.0s).
    output_video_path: Optional path for the output video file.
    mode: Clipping mode: "fast" (streamcopy) or "exact" (re-encoding).
    """

    video_path: str = Field(..., description="Path to the input video file.")
    start_time: int = Field(
        ..., description="Start timestamp in milliseconds (e.g., 10500 for 10.5s)."
    )
    end_time: int = Field(
        ..., description="End timestamp in milliseconds (e.g., 20000 for 20.0s)."
    )
    output_video_path: str | None = Field(
        None,
        description="Optional path for the output video file. If not provided, it will be generated based on the video path.",
    )
    mode: Literal["fast", "exact"] = Field(
        "fast",
        description="Clipping mode: 'fast' (streamcopy, keyframe-accurate) or 'exact' (re-encoding, frame-accurate).",
    )


class ClippingResponse(BaseModel):
    """
    Response model for the video clipping feature.

    video_path: Path to the clipped video file.
    success: bool
    """

    video_path: str = Field(..., description="Path to the clipped video file.")
    success: bool = Field(True, description="Indicates if the clipping was successful.")


class JumpCutRequest(BaseModel):
    """
    Request model for the jump cut feature.

    video_path: Path to the input video file.
    audio_path: Path to the input audio file used for silence detection.
    output_video_path: Optional path for the output video file.
    """

    video_path: str = Field(..., description="Path to the input video file.")
    audio_path: str = Field(
        ..., description="Path to the input audio file (e.g., extracted .mp3 or .wav)."
    )
    output_video_path: str | None = Field(
        None,
        description="Optional path for the output video file.",
    )


class JumpCutResponse(BaseModel):
    """
    Response model for the jump cut feature.

    video_path: Path to the output video file.
    success: Indicates if the process was successful.
    cut_count: Number of silences/cuts processed.
    """

    video_path: str = Field(..., description="Path to the output jump cut video file.")
    success: bool = Field(True, description="Indicates if the jump cut was successful.")
    cut_count: int = Field(0, description="Number of active voice segments extracted.")
