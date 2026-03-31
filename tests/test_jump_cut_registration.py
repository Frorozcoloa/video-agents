import pytest
from unittest.mock import patch
from fastmcp import FastMCP
from features.video_clipping.tool import register_video_clipping
from features.video_clipping.models import JumpCutResponse


@pytest.mark.anyio
async def test_jump_cut_tool_registration():
    """Verify that jump_cut_video tool is registered."""
    mcp = FastMCP("Test Server")
    register_video_clipping(mcp)

    tools = await mcp.list_tools()
    assert "jump_cut_video" in [tool.name for tool in tools]


@pytest.mark.anyio
@patch("features.video_clipping.tool.process_jump_cut")
async def test_jump_cut_tool_execution(mock_process):
    """Verify jump_cut_video tool delegates to process_jump_cut and returns video path."""
    mcp = FastMCP("Test Server")
    register_video_clipping(mcp)

    mock_process.return_value = JumpCutResponse(
        video_path="output_jumpcut.mp4", success=True, cut_count=3
    )

    result = await mcp.call_tool(
        "jump_cut_video",
        {"video_path": "input.mp4", "audio_path": "audio.mp3"},
    )
    assert "output_jumpcut.mp4" in result.content[0].text
    mock_process.assert_called_once()
