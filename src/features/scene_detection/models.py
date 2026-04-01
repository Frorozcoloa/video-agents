"""Models for the scene detection feature."""

from pydantic import BaseModel, Field


class Scene(BaseModel):
    scene_number: int = Field(..., description="1-based scene index.")
    start_ms: int = Field(..., description="Scene start timestamp in milliseconds.")
    end_ms: int = Field(..., description="Scene end timestamp in milliseconds.")


class SceneList(BaseModel):
    scenes: list[Scene] = Field(..., description="List of detected scenes.")
