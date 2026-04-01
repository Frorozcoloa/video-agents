"""Models for the B-roll overlay feature."""

from pydantic import BaseModel, Field, model_validator


class BrollRequest(BaseModel):
    """Model for a B-roll overlay request.

    Attributes:
        video_path: Path to the main video file.
        broll_path: Path to the B-roll clip to overlay.
        start_ms: Overlay start timestamp in milliseconds.
        end_ms: Overlay end timestamp in milliseconds.
        output_path: Output path. If omitted, generated with _broll suffix.
    """

    video_path: str = Field(..., description="Path to the main video file.")
    broll_path: str = Field(..., description="Path to the B-roll clip to overlay.")
    start_ms: int = Field(..., description="Overlay start timestamp in milliseconds.")
    end_ms: int = Field(..., description="Overlay end timestamp in milliseconds.")
    output_path: str | None = Field(
        None,
        description="Output path. If omitted, generated with _broll suffix.",
    )

    @model_validator(mode="after")
    def validate_timestamps(self) -> "BrollRequest":
        """Validate that start_ms is less than end_ms.

        Returns:
            BrollRequest: The validated BrollRequest.
        """
        if self.start_ms >= self.end_ms:
            raise ValueError("start_ms must be less than end_ms")
        return self
