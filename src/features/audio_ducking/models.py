"""Models for the audio ducking feature."""

from pydantic import BaseModel, Field, field_validator


class DuckingParams(BaseModel):
    """Compression parameters applied during ducking."""

    threshold: float
    ratio: float
    attack: int
    release: int


class AudioDuckingInput(BaseModel):
    """Input model for the audio ducking tool."""

    voice_path: str = Field(..., description="Path to the voice/voiceover audio file.")
    music_path: str = Field(..., description="Path to the background music audio file.")
    output_path: str = Field(..., description="Path for the mixed output audio file.")
    threshold: float = Field(
        0.1,
        description="Compression threshold (0.0–1.0). Ducking activates above this level.",
    )
    ratio: float = Field(
        5.0,
        description="Compression ratio (≥1.0). Higher values produce stronger ducking.",
    )
    attack: int = Field(
        20,
        description="Attack time in milliseconds (≥1). How quickly ducking engages.",
    )
    release: int = Field(
        500,
        description="Release time in milliseconds (≥1). How quickly music returns to full volume.",
    )

    @field_validator("threshold")
    @classmethod
    def threshold_in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("threshold must be between 0.0 and 1.0")
        return v

    @field_validator("ratio")
    @classmethod
    def ratio_minimum(cls, v: float) -> float:
        if v < 1.0:
            raise ValueError("ratio must be ≥ 1.0")
        return v

    @field_validator("attack", "release")
    @classmethod
    def positive_ms(cls, v: int) -> int:
        if v < 1:
            raise ValueError("attack and release must be ≥ 1 ms")
        return v


class AudioDuckingOutput(BaseModel):
    """Output model for the audio ducking tool."""

    output_path: str = Field(..., description="Path to the mixed output file.")
    params: DuckingParams = Field(..., description="Compression parameters applied.")
