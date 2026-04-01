"""Models for the scene detection feature."""

from pydantic import BaseModel, Field


class Scene(BaseModel):
    """Model for a detected scene

    Attributes:
        scene_number (int): 1-based scene index.
        start_ms (int): Scene start timestamp in milliseconds.
        end_ms (int): Scene end timestamp in milliseconds.
    """

    scene_number: int = Field(..., description="1-based scene index.")
    start_ms: int = Field(..., description="Scene start timestamp in milliseconds.")
    end_ms: int = Field(..., description="Scene end timestamp in milliseconds.")


class SceneList(BaseModel):
    """Model for a list of detected scenes

    Attributes:
        scenes (list[Scene]): List of detected scenes.
    """

    scenes: list[Scene] = Field(..., description="List of detected scenes.")
