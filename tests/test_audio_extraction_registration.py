import pytest
from unittest.mock import patch
from fastmcp import FastMCP
from features.audio_extraction.tool import register_audio_extraction


@pytest.mark.anyio
async def test_audio_extraction_tool_registration():
    """Verify that the tool is registered."""
    mcp = FastMCP("Test Server")
    register_audio_extraction(mcp)

    tools = await mcp.list_tools()
    assert "extract_audio" in [tool.name for tool in tools]


@pytest.mark.anyio
@patch("features.audio_extraction.tool.extract_audio_logic")
async def test_audio_extraction_tool_execution(mock_logic):
    """Verify tool execution calls logic."""
    mcp = FastMCP("Test Server")
    register_audio_extraction(mcp)

    from features.audio_extraction.models import ExtractionResponse

    mock_logic.return_value = ExtractionResponse(audio_path="test.mp3", success=True)

    result = await mcp.call_tool("extract_audio", {"video_path": "test.mp4"})
    assert "test.mp3" in result.content[0].text
    mock_logic.assert_called_once()
