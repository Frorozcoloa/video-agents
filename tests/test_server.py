import pytest
from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world
from features.hello_world.models import GreetingRequest
from features.hello_world.logic import generate_greeting


def test_server_initialization():
    """Verify the FastMCP server can be initialized."""
    mcp = FastMCP("Test Server")
    assert mcp.name == "Test Server"


def test_hello_world_logic():
    """Verify the greeting logic works correctly."""
    request = GreetingRequest(name="Gemini")
    response = generate_greeting(request)
    assert response.message == "Hello Gemini, Video Agent is ready."


@pytest.mark.anyio
async def test_tool_registration():
    """Verify the hello_world tool is registered."""
    mcp = FastMCP("Test Server")
    register_hello_world(mcp)

    # Check if the tool exists in the server
    tools = await mcp.list_tools()
    assert "hello_world" in [tool.name for tool in tools]
