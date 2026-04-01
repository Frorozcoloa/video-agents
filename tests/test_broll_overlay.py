"""Unit tests for B-roll overlay logic and MCP tool registration."""

import pytest
from unittest.mock import patch, MagicMock
from fastmcp import FastMCP
from pydantic import ValidationError
from features.broll_overlay.logic import apply_broll
from features.broll_overlay.models import BrollRequest
from features.broll_overlay.tool import register_broll_overlay


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_PROBE = {
    "streams": [
        {"codec_type": "video", "width": 1920, "height": 1080},
        {"codec_type": "audio"},
    ]
}


def _valid_request(**kwargs) -> BrollRequest:
    defaults = dict(
        video_path="main.mp4",
        broll_path="broll.mp4",
        start_ms=1000,
        end_ms=5000,
    )
    defaults.update(kwargs)
    return BrollRequest(**defaults)


def _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_ffmpeg_output):
    """Wire up MagicMock chain for ffmpeg.input / ffmpeg.filter / ffmpeg.output."""
    main_node = MagicMock()
    broll_node = MagicMock()

    # input() returns different nodes per call
    mock_input.side_effect = [main_node, broll_node]

    # video property → supports filter_multi_output and filter
    main_video = MagicMock()
    main_node.video = main_video
    main_node.audio = MagicMock()

    split = MagicMock()
    main_video.filter_multi_output.return_value = split
    main_v1 = MagicMock()
    main_v2 = MagicMock()
    split.stream.side_effect = lambda i: main_v1 if i == 0 else main_v2

    # Trim/filter chain on main_v1
    trimmed = MagicMock()
    main_v1.trim.return_value = trimmed
    segment = MagicMock()
    trimmed.filter.return_value = segment

    # Scale filter on broll video
    broll_video = MagicMock()
    broll_node.video = broll_video
    broll_scaled = MagicMock()
    broll_video.filter.return_value = broll_scaled

    # ffmpeg.filter calls
    overlaid = MagicMock()
    out_video = MagicMock()
    mock_ffmpeg_filter.side_effect = [overlaid, out_video]

    # ffmpeg.output chain
    output_node = MagicMock()
    mock_ffmpeg_output.return_value = output_node
    overwrite_node = MagicMock()
    output_node.overwrite_output.return_value = overwrite_node
    overwrite_node.run.return_value = (b"", b"")

    return {
        "main_node": main_node,
        "broll_node": broll_node,
        "main_v1": main_v1,
        "main_v2": main_v2,
        "segment": segment,
        "broll_scaled": broll_scaled,
        "overlaid": overlaid,
        "out_video": out_video,
        "output_node": output_node,
    }


# ---------------------------------------------------------------------------
# 6.2 — FFmpeg filter graph construction
# ---------------------------------------------------------------------------


@patch("features.broll_overlay.logic.ffmpeg.output")
@patch("features.broll_overlay.logic.ffmpeg.filter")
@patch("features.broll_overlay.logic.ffmpeg.input")
@patch("features.broll_overlay.logic.ffmpeg.probe", return_value=FAKE_PROBE)
@patch("os.path.exists", return_value=True)
def test_filter_graph_uses_overlay_and_scale(
    mock_exists, mock_probe, mock_input, mock_ffmpeg_filter, mock_output
):
    """Verify the filter graph contains overlay (with eof_action=repeat) and scale."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_request()

    apply_broll(request)

    # scale filter applied to B-roll video
    nodes["broll_node"].video.filter.assert_called_once_with("scale", 1920, 1080)

    # First ffmpeg.filter call: overlay with eof_action=repeat on the segment
    first_overlay_call = mock_ffmpeg_filter.call_args_list[0]
    assert first_overlay_call[0][1] == "overlay"
    assert first_overlay_call[1].get("eof_action") == "repeat"

    # Second ffmpeg.filter call: composite overlay with time-based enable
    second_overlay_call = mock_ffmpeg_filter.call_args_list[1]
    assert second_overlay_call[0][1] == "overlay"
    enable_str = second_overlay_call[1].get("enable", "")
    assert "between" in enable_str


@patch("features.broll_overlay.logic.ffmpeg.output")
@patch("features.broll_overlay.logic.ffmpeg.filter")
@patch("features.broll_overlay.logic.ffmpeg.input")
@patch("features.broll_overlay.logic.ffmpeg.probe", return_value=FAKE_PROBE)
@patch("os.path.exists", return_value=True)
def test_filter_graph_uses_trim_and_setpts(
    mock_exists, mock_probe, mock_input, mock_ffmpeg_filter, mock_output
):
    """Verify segment is trimmed and PTS reset via setpts."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_request(start_ms=2000, end_ms=8000)

    apply_broll(request)

    nodes["main_v1"].trim.assert_called_once_with(start=2.0, end=8.0)
    nodes["main_v1"].trim.return_value.filter.assert_called_once_with(
        "setpts", "PTS-STARTPTS"
    )


# ---------------------------------------------------------------------------
# 6.3 — Timestamp validation
# ---------------------------------------------------------------------------


def test_start_ms_equal_to_end_ms_raises():
    """ValidationError when start_ms == end_ms."""
    with pytest.raises(ValidationError):
        BrollRequest(
            video_path="main.mp4", broll_path="b.mp4", start_ms=5000, end_ms=5000
        )


def test_start_ms_greater_than_end_ms_raises():
    """ValidationError when start_ms > end_ms."""
    with pytest.raises(ValidationError):
        BrollRequest(
            video_path="main.mp4", broll_path="b.mp4", start_ms=9000, end_ms=1000
        )


# ---------------------------------------------------------------------------
# 6.4 — Default output path generation
# ---------------------------------------------------------------------------


@patch("features.broll_overlay.logic.ffmpeg.output")
@patch("features.broll_overlay.logic.ffmpeg.filter")
@patch("features.broll_overlay.logic.ffmpeg.input")
@patch("features.broll_overlay.logic.ffmpeg.probe", return_value=FAKE_PROBE)
@patch("os.path.exists", return_value=True)
def test_default_output_path_has_broll_suffix(
    mock_exists, mock_probe, mock_input, mock_ffmpeg_filter, mock_output
):
    """Output path defaults to input filename with _broll suffix."""
    _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_request(video_path="videos/main.mp4", output_path=None)

    result = apply_broll(request)

    assert result == "videos/main_broll.mp4"


@patch("features.broll_overlay.logic.ffmpeg.output")
@patch("features.broll_overlay.logic.ffmpeg.filter")
@patch("features.broll_overlay.logic.ffmpeg.input")
@patch("features.broll_overlay.logic.ffmpeg.probe", return_value=FAKE_PROBE)
@patch("os.path.exists", return_value=True)
def test_explicit_output_path_respected(
    mock_exists, mock_probe, mock_input, mock_ffmpeg_filter, mock_output
):
    """When output_path is provided, it is used as-is."""
    _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_request(output_path="/tmp/custom_out.mp4")

    result = apply_broll(request)

    assert result == "/tmp/custom_out.mp4"


# ---------------------------------------------------------------------------
# 6.5 — Audio preservation
# ---------------------------------------------------------------------------


@patch("features.broll_overlay.logic.ffmpeg.output")
@patch("features.broll_overlay.logic.ffmpeg.filter")
@patch("features.broll_overlay.logic.ffmpeg.input")
@patch("features.broll_overlay.logic.ffmpeg.probe", return_value=FAKE_PROBE)
@patch("os.path.exists", return_value=True)
def test_main_audio_passed_through(
    mock_exists, mock_probe, mock_input, mock_ffmpeg_filter, mock_output
):
    """ffmpeg.output receives main audio stream (B-roll audio discarded)."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_request()

    apply_broll(request)

    output_call_args = mock_output.call_args[0]
    # Second positional arg is audio stream (main_input.audio)
    assert output_call_args[1] is nodes["main_node"].audio
    # B-roll audio (broll_node.audio) must NOT appear in output args
    assert nodes["broll_node"].audio not in output_call_args


# ---------------------------------------------------------------------------
# Missing file errors
# ---------------------------------------------------------------------------


def test_missing_main_video_raises():
    """FileNotFoundError when main video does not exist."""
    request = _valid_request(video_path="missing.mp4")
    with pytest.raises(FileNotFoundError, match="Video not found"):
        apply_broll(request)


@patch("os.path.exists")
def test_missing_broll_raises(mock_exists):
    """FileNotFoundError when B-roll file does not exist."""
    mock_exists.side_effect = lambda p: p != "broll.mp4"
    request = _valid_request()
    with pytest.raises(FileNotFoundError, match="B-roll not found"):
        apply_broll(request)


# ---------------------------------------------------------------------------
# 6.6 — MCP tool registration
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_broll_overlay_tool_registration():
    """Verify register_broll_overlay registers the apply_broll tool."""
    mcp = FastMCP("Test Server")
    register_broll_overlay(mcp)

    tools = await mcp.list_tools()
    assert "apply_broll" in [t.name for t in tools]


@pytest.mark.anyio
@patch("features.broll_overlay.tool.apply_broll_logic")
async def test_broll_overlay_tool_execution(mock_logic):
    """Verify tool delegates to logic and returns toon-encoded output path."""
    mcp = FastMCP("Test Server")
    register_broll_overlay(mcp)

    mock_logic.return_value = "output_broll.mp4"

    result = await mcp.call_tool(
        "apply_broll",
        {
            "video_path": "main.mp4",
            "broll_path": "broll.mp4",
            "start_ms": 1000,
            "end_ms": 5000,
        },
    )
    assert "output_broll.mp4" in result.content[0].text
    mock_logic.assert_called_once()
