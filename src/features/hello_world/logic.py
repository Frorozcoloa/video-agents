from .models import GreetingRequest, GreetingResponse

def generate_greeting(request: GreetingRequest) -> GreetingResponse:
    """Implementation of the greeting logic."""
    return GreetingResponse(message=f"Hello {request.name}, Video Agent is ready.")
