from fastmcp import FastMCP
from .models import GreetingRequest
from .logic import generate_greeting


def register_hello_world(mcp: FastMCP):
    @mcp.tool()
    def hello_world(name: str) -> str:
        """Returns a greeting to confirm the server is operational."""
        request = GreetingRequest(name=name)
        response = generate_greeting(request)
        return response.message
