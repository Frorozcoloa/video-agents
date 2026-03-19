"""Models for the audio transcription feature."""

from pydantic import BaseModel, Field
from typing import List


class TranscriptionSegment(BaseModel):
    """
    Represents a segment of transcribed text with its start and end times.

    Args:
        texto: The transcribed word or segment
        tiempo_inicio: Start time in milliseconds
        tiempo_fin: End time in milliseconds
    """

    texto: str = Field(..., description="The transcribed word or segment")
    tiempo_inicio: int = Field(..., description="Start time in milliseconds")
    tiempo_fin: int = Field(..., description="End time in milliseconds")


class TranscriptionRequest(BaseModel):
    """
    Use this class to define the request for the audio transcription feature.

    Args:
        audio_path: The path to the audio file to transcribe
        model_size: Size of the Whisper model to load
    """

    audio_path: str = Field(..., description="The path to the audio file to transcribe")
    model_size: str = Field(
        "base", description="Whisper model size: base, small, medium, large"
    )


class TranscriptionResponse(BaseModel):
    """
    Use this class to define the response for the audio transcription feature.

    Args:
        segments: List of transcribed segments with timestamps
    """

    segments: List[TranscriptionSegment] = Field(
        ..., description="List of transcribed segments with timestamps"
    )
