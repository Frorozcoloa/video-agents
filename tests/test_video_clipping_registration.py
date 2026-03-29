import pytest
from unittest.mock import patch
from fastmcp import FastMCP
from features.video_clipping.tool import register_video_clipping


@pytest.mark.anyio
async def test_video_clipping_tool_registration():
    """Verify that the tool is registered."""
    mcp = FastMCP("Test Server")
    register_video_clipping(mcp)

    tools = await mcp.list_tools()
    assert "clip_video" in [tool.name for tool in tools]


@pytest.mark.anyio
@patch("features.video_clipping.tool.clip_video_logic")
async def test_video_clipping_tool_execution(mock_logic):
    """Verify tool execution calls logic."""
    mcp = FastMCP("Test Server")
    register_video_clipping(mcp)

    from features.video_clipping.models import ClippingResponse

    mock_logic.return_value = ClippingResponse(video_path="test_clip.mp4", success=True)

    result = await mcp.call_tool(
        "clip_video", {"video_path": "test.mp4", "start_time": 0, "end_time": 1000}
    )
    assert "test_clip.mp4" in result.content[0].text
    mock_logic.assert_called_once()
