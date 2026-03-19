import pytest
from unittest.mock import patch
from fastmcp import FastMCP
from features.audio_transcription.tool import register_audio_transcription


@pytest.mark.anyio
async def test_audio_transcription_registration():
    """Verify that the transcribe_audio tool is registered correctly in FastMCP."""
    mcp = FastMCP("Test")
    register_audio_transcription(mcp)

    # Check if tool is in mcp tools
    tools = await mcp.list_tools()
    assert "transcribe_audio" in [t.name for t in tools]

    # Verify tool description contains expected keywords
    tool = next(t for t in tools if t.name == "transcribe_audio")
    assert "transcribes" in tool.description.lower()
    assert "timestamps" in tool.description.lower()


@pytest.mark.anyio
@patch("features.audio_transcription.tool.transcribe_audio_logic")
async def test_audio_transcription_tool_execution(mock_logic):
    """Verify the transcribe_audio tool can be executed through the server."""
    mcp = FastMCP("Test")
    register_audio_transcription(mcp)

    # Setup mock
    mock_logic.return_value = [
        {"texto": "Hello", "tiempo_inicio": 0, "tiempo_fin": 1000}
    ]

    # Call the tool
    result = await mcp.call_tool("transcribe_audio", {"audio_path": "audio.mp3"})

    # result.content[0].text is a JSON string of the TranscriptionResponse
    import json

    data = json.loads(result.content[0].text)
    assert len(data["segments"]) == 1
    assert data["segments"][0]["texto"] == "Hello"
    mock_logic.assert_called_once_with(audio_path="audio.mp3", model_size="base")
