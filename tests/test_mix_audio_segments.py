"""Unit tests for mix audio segments logic and MCP tool registration."""

import pytest
from unittest.mock import patch, MagicMock
from fastmcp import FastMCP
from pydantic import ValidationError
from features.mix_audio_segments.logic import mix_audio_segments_logic
from features.mix_audio_segments.models import AudioSegment, MixAudioSegmentsInput
from features.mix_audio_segments.tool import register_mix_audio_segments


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seg(audio_path="seg.wav", start_ms=0, end_ms=5000) -> dict:
    return {"audio_path": audio_path, "start_ms": start_ms, "end_ms": end_ms}


def _valid_input(**kwargs) -> MixAudioSegmentsInput:
    defaults = dict(
        video_path="video.mp4",
        segments=[AudioSegment(**_seg())],
        output_path="output.mp4",
    )
    defaults.update(kwargs)
    return MixAudioSegmentsInput(**defaults)


def _setup_ffmpeg_chain(
    mock_input, mock_ffmpeg_filter, mock_ffmpeg_output, n_segments=1
):
    """Wire up MagicMock chain for the mix audio segments filter graph."""
    video_node = MagicMock()
    seg_nodes = [MagicMock() for _ in range(n_segments)]

    # First call → video, subsequent calls → segment audio inputs
    mock_input.side_effect = [video_node] + seg_nodes

    # video.audio and video.video
    video_audio = MagicMock()
    video_video = MagicMock()
    video_node.audio = video_audio
    video_node.video = video_video

    # Each segment node: .audio.filter("atrim").filter("adelay")
    delayed_streams = []
    for node in seg_nodes:
        seg_audio = MagicMock()
        node.audio = seg_audio
        trimmed = MagicMock()
        delayed = MagicMock()
        seg_audio.filter.return_value = trimmed
        trimmed.filter.return_value = delayed
        delayed_streams.append((seg_audio, trimmed, delayed))

    # ffmpeg.filter → mixed stream
    mixed = MagicMock()
    mock_ffmpeg_filter.return_value = mixed

    # ffmpeg.output chain
    output_node = MagicMock()
    mock_ffmpeg_output.return_value = output_node
    overwrite_node = MagicMock()
    output_node.overwrite_output.return_value = overwrite_node
    overwrite_node.run.return_value = (b"", b"")

    return {
        "video_node": video_node,
        "video_audio": video_audio,
        "video_video": video_video,
        "seg_nodes": seg_nodes,
        "delayed_streams": delayed_streams,
        "mixed": mixed,
    }


# ---------------------------------------------------------------------------
# 3.1 — MCP tool registration
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_mix_audio_segments_tool_registered():
    """Verify register_mix_audio_segments registers the mix_audio_segments tool."""
    mcp = FastMCP("Test Server")
    register_mix_audio_segments(mcp)

    tools = await mcp.list_tools()
    assert "mix_audio_segments" in [t.name for t in tools]


# ---------------------------------------------------------------------------
# 3.2 — Single segment: atrim, adelay, amix with normalize=0
# ---------------------------------------------------------------------------


@patch("features.mix_audio_segments.logic.ffmpeg.output")
@patch("features.mix_audio_segments.logic.ffmpeg.filter")
@patch("features.mix_audio_segments.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_single_segment_uses_atrim_adelay_amix(
    mock_exists, mock_isdir, mock_input, mock_filter, mock_output
):
    """atrim, adelay and amix(normalize=0) appear in the filter graph for 1 segment."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_filter, mock_output, n_segments=1)
    request = _valid_input(
        segments=[AudioSegment(audio_path="seg.wav", start_ms=2000, end_ms=7000)]
    )

    mix_audio_segments_logic(request)

    seg_audio, trimmed, delayed = nodes["delayed_streams"][0]

    # atrim with correct duration
    seg_audio.filter.assert_called_once_with("atrim", duration=5.0)
    # adelay with correct start
    trimmed.filter.assert_called_once_with("adelay", "2000|2000")

    # amix with normalize=0
    amix_call = mock_filter.call_args
    assert amix_call[0][1] == "amix"
    assert amix_call[1].get("normalize") == 0


# ---------------------------------------------------------------------------
# 3.3 — Multiple segments: amix inputs = N + 1
# ---------------------------------------------------------------------------


@patch("features.mix_audio_segments.logic.ffmpeg.output")
@patch("features.mix_audio_segments.logic.ffmpeg.filter")
@patch("features.mix_audio_segments.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_multiple_segments_amix_inputs_count(
    mock_exists, mock_isdir, mock_input, mock_filter, mock_output
):
    """amix receives inputs=N+1 where N is the number of segments."""
    n = 3
    _setup_ffmpeg_chain(mock_input, mock_filter, mock_output, n_segments=n)
    segments = [
        AudioSegment(audio_path="s.wav", start_ms=i * 1000, end_ms=i * 1000 + 500)
        for i in range(n)
    ]
    request = _valid_input(segments=segments)

    mix_audio_segments_logic(request)

    amix_call = mock_filter.call_args
    assert amix_call[1].get("inputs") == n + 1  # original + N segments


# ---------------------------------------------------------------------------
# replace_original=True — only segments, no original audio
# ---------------------------------------------------------------------------


@patch("features.mix_audio_segments.logic.ffmpeg.output")
@patch("features.mix_audio_segments.logic.ffmpeg.filter")
@patch("features.mix_audio_segments.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_replace_original_excludes_original_audio(
    mock_exists, mock_isdir, mock_input, mock_filter, mock_output
):
    """When replace_original=True, amix receives only segments (inputs=N, not N+1)."""
    n = 2
    _setup_ffmpeg_chain(mock_input, mock_filter, mock_output, n_segments=n)
    segments = [
        AudioSegment(audio_path="s.wav", start_ms=i * 1000, end_ms=i * 1000 + 500)
        for i in range(n)
    ]
    request = _valid_input(segments=segments, replace_original=True)

    mix_audio_segments_logic(request)

    amix_call = mock_filter.call_args
    assert amix_call[1].get("inputs") == n  # only segments, original excluded


# ---------------------------------------------------------------------------
# 3.4 — Segment trimmed to correct duration
# ---------------------------------------------------------------------------


@patch("features.mix_audio_segments.logic.ffmpeg.output")
@patch("features.mix_audio_segments.logic.ffmpeg.filter")
@patch("features.mix_audio_segments.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_atrim_duration_computed_from_segment(
    mock_exists, mock_isdir, mock_input, mock_filter, mock_output
):
    """atrim duration = (end_ms - start_ms) / 1000."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_filter, mock_output, n_segments=1)
    request = _valid_input(
        segments=[AudioSegment(audio_path="seg.wav", start_ms=3000, end_ms=8500)]
    )

    mix_audio_segments_logic(request)

    seg_audio = nodes["delayed_streams"][0][0]
    seg_audio.filter.assert_called_once_with("atrim", duration=5.5)


# ---------------------------------------------------------------------------
# 3.5 — Segment delayed to correct start
# ---------------------------------------------------------------------------


@patch("features.mix_audio_segments.logic.ffmpeg.output")
@patch("features.mix_audio_segments.logic.ffmpeg.filter")
@patch("features.mix_audio_segments.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_adelay_uses_start_ms(
    mock_exists, mock_isdir, mock_input, mock_filter, mock_output
):
    """adelay is called with start_ms value on all channels."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_filter, mock_output, n_segments=1)
    request = _valid_input(
        segments=[AudioSegment(audio_path="seg.wav", start_ms=12000, end_ms=15000)]
    )

    mix_audio_segments_logic(request)

    trimmed = nodes["delayed_streams"][0][1]
    trimmed.filter.assert_called_once_with("adelay", "12000|12000")


# ---------------------------------------------------------------------------
# 3.6 — Default output path
# ---------------------------------------------------------------------------


@patch("features.mix_audio_segments.logic.ffmpeg.output")
@patch("features.mix_audio_segments.logic.ffmpeg.filter")
@patch("features.mix_audio_segments.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_default_output_path_has_mixed_suffix(
    mock_exists, mock_isdir, mock_input, mock_filter, mock_output
):
    """Output defaults to {stem}_mixed{ext} when not provided."""
    _setup_ffmpeg_chain(mock_input, mock_filter, mock_output)
    request = _valid_input(video_path="projects/clip.mp4", output_path=None)

    result = mix_audio_segments_logic(request)

    assert result.output_path == "projects/clip_mixed.mp4"


# ---------------------------------------------------------------------------
# 3.7 — Validation errors
# ---------------------------------------------------------------------------


def test_empty_segments_raises():
    """ValidationError when segments list is empty."""
    with pytest.raises(ValidationError):
        MixAudioSegmentsInput(video_path="v.mp4", segments=[])


def test_start_ms_equal_end_ms_raises():
    """ValidationError when start_ms == end_ms."""
    with pytest.raises(ValidationError):
        AudioSegment(audio_path="a.wav", start_ms=5000, end_ms=5000)


def test_start_ms_greater_than_end_ms_raises():
    """ValidationError when start_ms > end_ms."""
    with pytest.raises(ValidationError):
        AudioSegment(audio_path="a.wav", start_ms=9000, end_ms=1000)


def test_negative_start_ms_raises():
    """ValidationError when start_ms < 0."""
    with pytest.raises(ValidationError):
        AudioSegment(audio_path="a.wav", start_ms=-500, end_ms=1000)


# ---------------------------------------------------------------------------
# 3.8 — Missing video file
# ---------------------------------------------------------------------------


def test_missing_video_raises_without_ffmpeg():
    """FileNotFoundError when video does not exist; FFmpeg is never called."""
    request = _valid_input(video_path="missing.mp4")
    with patch("features.mix_audio_segments.logic.ffmpeg.input") as mock_input:
        with pytest.raises(FileNotFoundError, match="Video file not found"):
            mix_audio_segments_logic(request)
        mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# 3.9 — Missing segment audio file
# ---------------------------------------------------------------------------


@patch("os.path.exists")
def test_missing_segment_audio_raises_without_ffmpeg(mock_exists):
    """FileNotFoundError when a segment audio file does not exist."""
    mock_exists.side_effect = lambda p: p != "seg.wav"
    request = _valid_input()
    with patch("features.mix_audio_segments.logic.ffmpeg.input") as mock_input:
        with pytest.raises(FileNotFoundError, match="Segment audio file not found"):
            mix_audio_segments_logic(request)
        mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# 3.10 — Non-existent output directory
# ---------------------------------------------------------------------------


@patch("os.path.isdir", return_value=False)
@patch("os.path.exists", return_value=True)
def test_nonexistent_output_dir_raises_without_ffmpeg(mock_exists, mock_isdir):
    """NotADirectoryError when output directory does not exist."""
    request = _valid_input(output_path="/nonexistent/dir/out.mp4")
    with patch("features.mix_audio_segments.logic.ffmpeg.input") as mock_input:
        with pytest.raises(NotADirectoryError, match="Output directory does not exist"):
            mix_audio_segments_logic(request)
        mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# Tool execution (toon-format output)
# ---------------------------------------------------------------------------


@pytest.mark.anyio
@patch("features.mix_audio_segments.tool.mix_audio_segments_logic")
async def test_mix_audio_segments_tool_execution(mock_logic):
    """Verify tool delegates to logic and returns toon-encoded output."""
    from features.mix_audio_segments.models import MixAudioSegmentsOutput

    mcp = FastMCP("Test Server")
    register_mix_audio_segments(mcp)

    mock_logic.return_value = MixAudioSegmentsOutput(
        output_path="result.mp4", segments_count=2
    )

    result = await mcp.call_tool(
        "mix_audio_segments",
        {
            "video_path": "video.mp4",
            "segments": [
                {"audio_path": "a.wav", "start_ms": 0, "end_ms": 3000},
                {"audio_path": "b.wav", "start_ms": 5000, "end_ms": 8000},
            ],
        },
    )
    assert "result.mp4" in result.content[0].text
    assert mock_logic.call_count == 1
