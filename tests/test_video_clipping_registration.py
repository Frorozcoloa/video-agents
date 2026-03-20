import pytest
from unittest.mock import patch
from fastmcp import FastMCP
from features.video_clipping.tool import register_video_clipping


@pytest.mark.anyio
async def test_video_clipping_tool_execution():
    """Verify that the video clipping tool can be executed through the server."""
    mcp = FastMCP("Test Server")
    register_video_clipping(mcp)

    # Mock the logic to avoid FFmpeg calls
    with patch("features.video_clipping.tool.clip_video_logic") as mock_logic:
        from features.video_clipping.models import ClippingResponse

        mock_logic.return_value = ClippingResponse(
            video_path="output.mp4", success=True
        )

        result = await mcp.call_tool(
            "clip_video", {"video_path": "test.mp4", "start_time": 0, "end_time": 10}
        )

        assert "output.mp4" in result.content[0].text
        mock_logic.assert_called_once()
