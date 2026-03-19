import pytest
from unittest.mock import patch
from fastmcp import FastMCP
from features.audio_extraction.tool import register_audio_extraction
from features.audio_extraction.models import ExtractionResponse


@pytest.mark.anyio
async def test_extract_audio_tool_registration():
    """Verify the extract_audio tool is registered."""
    mcp = FastMCP("Test Server")
    register_audio_extraction(mcp)

    # Check if the tool exists in the server
    tools = await mcp.list_tools()
    assert "extract_audio" in [tool.name for tool in tools]


@pytest.mark.anyio
@patch("features.audio_extraction.tool.extract_audio_logic")
async def test_extract_audio_tool_execution(mock_logic):
    """Verify the extract_audio tool can be executed through the server."""
    mcp = FastMCP("Test Server")
    register_audio_extraction(mcp)

    # Setup mock
    mock_logic.return_value = ExtractionResponse(audio_path="output.mp3", success=True)

    # Call the tool
    result = await mcp.call_tool("extract_audio", {"video_path": "video.mp4"})

    assert result.content[0].text == "output.mp3"
    mock_logic.assert_called_once()
    # Check parameters
    request = mock_logic.call_args[0][0]
    assert request.video_path == "video.mp4"
    assert request.output_audio_path is None
