import pytest
from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world
from features.hello_world.models import GreetingRequest
from features.hello_world.logic import generate_greeting
from server import mcp


def test_server_instance_initialization():
    """Verify the actual server instance from src/server.py is correctly initialized."""
    assert mcp.name == "Video Agents"


@pytest.mark.anyio
async def test_hello_world_tool_execution():
    """Verify the hello_world tool can be executed through the server."""
    tools = await mcp.list_tools()
    next(t for t in tools if t.name == "hello_world")
    result = await mcp.call_tool("hello_world", {"name": "Tester"})
    assert "Hello Tester" in result.content[0].text


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
