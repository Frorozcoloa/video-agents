import pytest
from fastmcp import FastMCP
from features.audio_extraction.tool import register_audio_extraction


@pytest.mark.anyio
async def test_extract_audio_tool_registration():
    """Verify the extract_audio tool is registered."""
    mcp = FastMCP("Test Server")
    register_audio_extraction(mcp)

    # Check if the tool exists in the server
    tools = await mcp.list_tools()
    assert "extract_audio" in [tool.name for tool in tools]
