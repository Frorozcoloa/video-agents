"""Unit tests for scene detection logic and MCP resource registration."""

import pytest
from unittest.mock import patch, MagicMock
from fastmcp import FastMCP
from features.scene_detection.logic import detect_scenes
from features.scene_detection.tool import register_scene_detection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_timecode(seconds: float) -> MagicMock:
    tc = MagicMock()
    tc.get_seconds.return_value = seconds
    return tc


def _mock_video(duration_seconds: float = 10.0) -> MagicMock:
    video = MagicMock()
    video.duration.get_seconds.return_value = duration_seconds
    return video


def _setup_scene_manager(mock_sm_cls, scene_list, video):
    manager = MagicMock()
    mock_sm_cls.return_value = manager
    manager.get_scene_list.return_value = scene_list
    return manager


# ---------------------------------------------------------------------------
# 3.2 — ms conversion from FrameTimecode objects
# ---------------------------------------------------------------------------


@patch("features.scene_detection.logic.open_video")
@patch("features.scene_detection.logic.SceneManager")
@patch("os.path.exists", return_value=True)
def test_ms_conversion_from_frametimecode(mock_exists, mock_sm_cls, mock_open_video):
    """Verify that FrameTimecode values are correctly converted to milliseconds."""
    video = _mock_video()
    mock_open_video.return_value = video

    scene_list = [
        (_make_timecode(0.0), _make_timecode(5.5)),
        (_make_timecode(5.5), _make_timecode(12.3)),
    ]
    _setup_scene_manager(mock_sm_cls, scene_list, video)

    scenes = detect_scenes("test.mp4")

    assert len(scenes) == 2
    assert scenes[0].scene_number == 1
    assert scenes[0].start_ms == 0
    assert scenes[0].end_ms == 5500
    assert scenes[1].scene_number == 2
    assert scenes[1].start_ms == 5500
    assert scenes[1].end_ms == 12300


# ---------------------------------------------------------------------------
# 3.3 — Single-scene fallback
# ---------------------------------------------------------------------------


@patch("features.scene_detection.logic.open_video")
@patch("features.scene_detection.logic.SceneManager")
@patch("os.path.exists", return_value=True)
def test_single_scene_fallback_no_cuts(mock_exists, mock_sm_cls, mock_open_video):
    """If no cuts detected, return one scene covering the full duration."""
    video = _mock_video(duration_seconds=10.0)
    mock_open_video.return_value = video
    _setup_scene_manager(mock_sm_cls, [], video)

    scenes = detect_scenes("test.mp4")

    assert len(scenes) == 1
    assert scenes[0].scene_number == 1
    assert scenes[0].start_ms == 0
    assert scenes[0].end_ms == 10000


@patch("features.scene_detection.logic.open_video")
@patch("features.scene_detection.logic.SceneManager")
@patch("os.path.exists", return_value=True)
def test_single_scene_fractional_duration(mock_exists, mock_sm_cls, mock_open_video):
    """Single-scene duration uses int cast, truncating fractional ms."""
    video = _mock_video(duration_seconds=7.777)
    mock_open_video.return_value = video
    _setup_scene_manager(mock_sm_cls, [], video)

    scenes = detect_scenes("test.mp4")

    assert scenes[0].end_ms == 7777


# ---------------------------------------------------------------------------
# 3.4 — Error cases
# ---------------------------------------------------------------------------


def test_missing_file_raises_file_not_found():
    """FileNotFoundError raised when the video file does not exist."""
    with pytest.raises(FileNotFoundError, match="Video file not found"):
        detect_scenes("nonexistent.mp4")


@patch("features.scene_detection.logic.open_video")
@patch("os.path.exists", return_value=True)
def test_unreadable_video_raises_value_error(mock_exists, mock_open_video):
    """ValueError raised when PySceneDetect cannot read the video."""
    mock_open_video.side_effect = Exception("cannot decode")

    with pytest.raises(ValueError, match="Could not read video file"):
        detect_scenes("corrupt.mp4")


# ---------------------------------------------------------------------------
# 3.5 — MCP resource registration
# ---------------------------------------------------------------------------


@pytest.mark.anyio
@patch("features.scene_detection.tool.detect_scenes")
async def test_scene_detection_resource_registration(mock_detect):
    """Verify register_scene_detection registers a resource on the MCP server."""
    mcp = FastMCP("Test Server")
    register_scene_detection(mcp)

    mock_detect.return_value = []

    # FastMCP exposes resource templates via list_resource_templates
    templates = await mcp.list_resource_templates()
    uris = [t.uri_template for t in templates]
    assert any("scenes" in uri for uri in uris)
