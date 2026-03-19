"""Models for the audio extraction feature."""

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """
    Use this class to define the request for the audio extraction feature.

    video_path: Path
    output_audio_path: Path | None
    """

    video_path: str = Field(..., description="Path to the input video file.")
    output_audio_path: str | None = Field(
        None,
        description="Optional path for the output audio file. If not provided, it will be generated based on the video path.",
    )


class ExtractionResponse(BaseModel):
    """
    Use this class to define the response for the audio extraction feature.

    audio_path: Path
    success: bool
    """

    audio_path: str = Field(..., description="Path to the extracted audio file.")
    success: bool = Field(
        True, description="Indicates if the extraction was successful."
    )
