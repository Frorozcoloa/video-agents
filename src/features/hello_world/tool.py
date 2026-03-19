"""Tool for the hello world feature."""

from fastmcp import FastMCP
from .models import GreetingRequest
from .logic import generate_greeting


def register_hello_world(mcp: FastMCP):
    """
    Register the hello world tool with the MCP server.

    Args:
        mcp: The MCP server instance.
    """

    @mcp.tool()
    def hello_world(name: str) -> str:
        """Returns a greeting to confirm the server is operational.

        Args:
            name: The name to greet.

        Returns:
            str: The greeting message.
        """
        request = GreetingRequest(name=name)
        response = generate_greeting(request)
        return response.message
