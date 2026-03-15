from pydantic import BaseModel, Field

class GreetingRequest(BaseModel):
    name: str = Field(..., description="The name to greet")

    model_config = {
        "extra": "forbid",
        "strict": True
    }

class GreetingResponse(BaseModel):
    message: str = Field(..., description="The greeting message")
