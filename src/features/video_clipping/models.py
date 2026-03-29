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
