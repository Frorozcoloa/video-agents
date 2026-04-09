"""Models for the mix audio segments feature."""

from pydantic import BaseModel, Field, field_validator, model_validator


class AudioSegment(BaseModel):
    """A single timed audio segment to mix into the video."""

    audio_path: str = Field(..., description="Path to the audio file for this segment.")
    start_ms: int = Field(
        ..., description="Start position in the video (milliseconds)."
    )
    end_ms: int = Field(..., description="End position in the video (milliseconds).")

    @field_validator("start_ms")
    @classmethod
    def start_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("start_ms must be >= 0")
        return v

    @model_validator(mode="after")
    def end_after_start(self) -> "AudioSegment":
        if self.end_ms <= self.start_ms:
            raise ValueError("end_ms must be greater than start_ms")
        return self


class MixAudioSegmentsInput(BaseModel):
    """Input model for the mix audio segments tool."""

    video_path: str = Field(..., description="Path to the input video file.")
    segments: list[AudioSegment] = Field(
        ...,
        description="List of timed audio segments to mix into the video.",
        min_length=1,
    )
    output_path: str | None = Field(
        None,
        description="Path for the output video file. Defaults to input path with '_mixed' suffix.",
    )
    replace_original: bool = Field(
        False,
        description="If True, silence the original video audio and use only the provided segments.",
    )


class MixAudioSegmentsOutput(BaseModel):
    """Output model for the mix audio segments tool."""

    output_path: str = Field(..., description="Path to the output video file.")
    segments_count: int = Field(..., description="Number of audio segments mixed in.")
