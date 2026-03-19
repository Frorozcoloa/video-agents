"""Models for the hello world feature."""

from pydantic import BaseModel, Field


class GreetingRequest(BaseModel):
    """
    Use this class to define the request for the hello world feature.

    name: str
    """

    name: str = Field(..., description="The name to greet")

    model_config = {"extra": "forbid", "strict": True}


class GreetingResponse(BaseModel):
    """
    Use this class to define the response for the hello world feature.

    message: str
    """

    message: str = Field(..., description="The greeting message")
