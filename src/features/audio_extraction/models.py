from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    video_path: str = Field(..., description="Path to the input video file.")
    output_audio_path: str | None = Field(
        None,
        description="Optional path for the output audio file. If not provided, it will be generated based on the video path.",
    )


class ExtractionResponse(BaseModel):
    audio_path: str = Field(..., description="Path to the extracted audio file.")
    success: bool = Field(
        True, description="Indicates if the extraction was successful."
    )
