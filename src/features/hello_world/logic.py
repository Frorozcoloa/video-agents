"""Logic for the hello world feature."""

from .models import GreetingRequest, GreetingResponse


def generate_greeting(request: GreetingRequest) -> GreetingResponse:
    """Implementation of the greeting logic.

    Args:
        request: GreetingRequest object containing the name to greet.

    Returns:
        GreetingResponse object containing the greeting message.
    """
    return GreetingResponse(message=f"Hello {request.name}, Video Agent is ready.")
