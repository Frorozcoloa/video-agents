import pytest
from unittest.mock import patch
from fastmcp import FastMCP
from features.audio_transcription.tool import register_audio_transcription


@pytest.mark.anyio
async def test_audio_transcription_tool_registration():
    """Verify that the transcribe_audio tool is correctly registered."""
    mcp = FastMCP("Test Server")
    register_audio_transcription(mcp)

    tools = await mcp.list_tools()
    tool = next((t for t in tools if t.name == "transcribe_audio"), None)

    assert tool is not None
    assert "TOON" in tool.description


@pytest.mark.anyio
@patch("features.audio_transcription.tool.transcribe_audio_logic")
async def test_transcribe_audio_tool_execution(mock_logic):
    """Verify that the tool correctly calls the logic function."""
    mcp = FastMCP("Test Server")
    register_audio_transcription(mcp)

    mock_logic.return_value = "toon_data"

    result = await mcp.call_tool("transcribe_audio", {"audio_path": "test.wav"})
    assert result.content[0].text == "toon_data"
    mock_logic.assert_called_once()
