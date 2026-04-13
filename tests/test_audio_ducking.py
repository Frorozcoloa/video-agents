"""Unit tests for audio ducking logic and MCP tool registration."""

import pytest
from unittest.mock import patch, MagicMock
from fastmcp import FastMCP
from pydantic import ValidationError
from features.audio_ducking.logic import duck_audio
from features.audio_ducking.models import AudioDuckingInput
from features.audio_ducking.tool import register_audio_ducking


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid_input(**kwargs) -> AudioDuckingInput:
    defaults = dict(
        voice_path="voice.wav",
        music_path="music.mp3",
        output_path="mixed.wav",
    )
    defaults.update(kwargs)
    return AudioDuckingInput(**defaults)


def _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_ffmpeg_output):
    """Wire up MagicMock chain for the audio ducking filter graph."""
    voice_node = MagicMock()
    music_node = MagicMock()
    mock_input.side_effect = [voice_node, music_node]

    # .audio.filter("aformat", ...) chains
    voice_audio = MagicMock()
    music_audio = MagicMock()
    voice_node.audio = voice_audio
    music_node.audio = music_audio

    voice_stereo = MagicMock()
    music_stereo = MagicMock()
    voice_audio.filter.return_value = voice_stereo
    music_audio.filter.return_value = music_stereo

    # asplit → stream(0) = sc_trigger, stream(1) = voice_pass
    voice_split = MagicMock()
    voice_stereo.filter_multi_output.return_value = voice_split
    sc_trigger = MagicMock()
    voice_pass = MagicMock()
    voice_split.stream.side_effect = lambda i: sc_trigger if i == 0 else voice_pass

    # sidechaincompress → ducked_music; amix → mixed
    ducked_music = MagicMock()
    mixed = MagicMock()
    mock_ffmpeg_filter.side_effect = [ducked_music, mixed]

    # ffmpeg.output chain
    output_node = MagicMock()
    mock_ffmpeg_output.return_value = output_node
    overwrite_node = MagicMock()
    output_node.overwrite_output.return_value = overwrite_node
    overwrite_node.run.return_value = (b"", b"")

    return {
        "voice_node": voice_node,
        "music_node": music_node,
        "voice_stereo": voice_stereo,
        "music_stereo": music_stereo,
        "voice_split": voice_split,
        "sc_trigger": sc_trigger,
        "voice_pass": voice_pass,
        "ducked_music": ducked_music,
        "mixed": mixed,
    }


# ---------------------------------------------------------------------------
# 3.1 — MCP tool registration
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_audio_ducking_tool_registered():
    """Verify register_audio_ducking registers the audio_ducking tool."""
    mcp = FastMCP("Test Server")
    register_audio_ducking(mcp)

    tools = await mcp.list_tools()
    assert "audio_ducking" in [t.name for t in tools]


# ---------------------------------------------------------------------------
# 3.2 — Filter graph construction
# ---------------------------------------------------------------------------


@patch("features.audio_ducking.logic.ffmpeg.output")
@patch("features.audio_ducking.logic.ffmpeg.filter")
@patch("features.audio_ducking.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_filter_graph_uses_sidechaincompress_and_amix(
    mock_exists, mock_isdir, mock_input, mock_ffmpeg_filter, mock_output
):
    """Verify filter graph contains sidechaincompress and amix."""
    _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_input()

    duck_audio(request)

    # First ffmpeg.filter call: sidechaincompress
    first_call = mock_ffmpeg_filter.call_args_list[0]
    assert first_call[0][1] == "sidechaincompress"

    # Second ffmpeg.filter call: amix
    second_call = mock_ffmpeg_filter.call_args_list[1]
    assert second_call[0][1] == "amix"
    assert second_call[1].get("inputs") == 2


@patch("features.audio_ducking.logic.ffmpeg.output")
@patch("features.audio_ducking.logic.ffmpeg.filter")
@patch("features.audio_ducking.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_aformat_stereo_applied_to_both_inputs(
    mock_exists, mock_isdir, mock_input, mock_ffmpeg_filter, mock_output
):
    """Verify aformat=stereo is applied to both voice and music streams."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_input()

    duck_audio(request)

    nodes["voice_node"].audio.filter.assert_called_once_with(
        "aformat", channel_layouts="stereo"
    )
    nodes["music_node"].audio.filter.assert_called_once_with(
        "aformat", channel_layouts="stereo"
    )


@patch("features.audio_ducking.logic.ffmpeg.output")
@patch("features.audio_ducking.logic.ffmpeg.filter")
@patch("features.audio_ducking.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_voice_asplit_into_two_streams(
    mock_exists, mock_isdir, mock_input, mock_ffmpeg_filter, mock_output
):
    """Verify voice is split into two streams via asplit."""
    nodes = _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_input()

    duck_audio(request)

    nodes["voice_stereo"].filter_multi_output.assert_called_once_with("asplit", 2)


# ---------------------------------------------------------------------------
# 3.3 — Default parameters
# ---------------------------------------------------------------------------


@patch("features.audio_ducking.logic.ffmpeg.output")
@patch("features.audio_ducking.logic.ffmpeg.filter")
@patch("features.audio_ducking.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_default_parameters_passed_to_sidechaincompress(
    mock_exists, mock_isdir, mock_input, mock_ffmpeg_filter, mock_output
):
    """Verify defaults threshold=0.1, ratio=5, attack=20, release=500 are used."""
    _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_input()

    duck_audio(request)

    sc_call = mock_ffmpeg_filter.call_args_list[0]
    assert sc_call[1]["threshold"] == 0.1
    assert sc_call[1]["ratio"] == 5.0
    assert sc_call[1]["attack"] == 20
    assert sc_call[1]["release"] == 500


# ---------------------------------------------------------------------------
# 3.4 — Custom parameters
# ---------------------------------------------------------------------------


@patch("features.audio_ducking.logic.ffmpeg.output")
@patch("features.audio_ducking.logic.ffmpeg.filter")
@patch("features.audio_ducking.logic.ffmpeg.input")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
def test_custom_parameters_override_defaults(
    mock_exists, mock_isdir, mock_input, mock_ffmpeg_filter, mock_output
):
    """Verify caller-supplied values override defaults in the filter graph."""
    _setup_ffmpeg_chain(mock_input, mock_ffmpeg_filter, mock_output)
    request = _valid_input(threshold=0.05, ratio=8.0, attack=10, release=300)

    duck_audio(request)

    sc_call = mock_ffmpeg_filter.call_args_list[0]
    assert sc_call[1]["threshold"] == 0.05
    assert sc_call[1]["ratio"] == 8.0
    assert sc_call[1]["attack"] == 10
    assert sc_call[1]["release"] == 300


# ---------------------------------------------------------------------------
# 3.5 — Validation errors
# ---------------------------------------------------------------------------


def test_threshold_above_one_raises():
    """ValidationError when threshold > 1.0."""
    with pytest.raises(ValidationError):
        AudioDuckingInput(
            voice_path="v.wav", music_path="m.mp3", output_path="o.wav", threshold=1.5
        )


def test_threshold_below_zero_raises():
    """ValidationError when threshold < 0.0."""
    with pytest.raises(ValidationError):
        AudioDuckingInput(
            voice_path="v.wav", music_path="m.mp3", output_path="o.wav", threshold=-0.1
        )


def test_ratio_below_one_raises():
    """ValidationError when ratio < 1.0."""
    with pytest.raises(ValidationError):
        AudioDuckingInput(
            voice_path="v.wav", music_path="m.mp3", output_path="o.wav", ratio=0.5
        )


# ---------------------------------------------------------------------------
# 3.6 — Missing voice file
# ---------------------------------------------------------------------------


def test_missing_voice_file_raises_without_ffmpeg():
    """FileNotFoundError when voice file does not exist; FFmpeg is never called."""
    request = _valid_input(voice_path="nonexistent_voice.wav")
    with patch("features.audio_ducking.logic.ffmpeg.input") as mock_input:
        with pytest.raises(FileNotFoundError, match="Voice file not found"):
            duck_audio(request)
        mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# 3.7 — Missing music file
# ---------------------------------------------------------------------------


@patch("os.path.exists")
def test_missing_music_file_raises_without_ffmpeg(mock_exists):
    """FileNotFoundError when music file does not exist; FFmpeg is never called."""
    mock_exists.side_effect = lambda p: p != "music.mp3"
    request = _valid_input()
    with patch("features.audio_ducking.logic.ffmpeg.input") as mock_input:
        with pytest.raises(FileNotFoundError, match="Music file not found"):
            duck_audio(request)
        mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# 3.8 — Non-existent output directory
# ---------------------------------------------------------------------------


@patch("os.path.isdir", return_value=False)
@patch("os.path.exists", return_value=True)
def test_nonexistent_output_dir_raises_without_ffmpeg(mock_exists, mock_isdir):
    """NotADirectoryError when output directory does not exist; FFmpeg is never called."""
    request = _valid_input(output_path="/nonexistent/dir/out.wav")
    with patch("features.audio_ducking.logic.ffmpeg.input") as mock_input:
        with pytest.raises(NotADirectoryError, match="Output directory does not exist"):
            duck_audio(request)
        mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# Tool execution (toon-format output)
# ---------------------------------------------------------------------------


@pytest.mark.anyio
@patch("features.audio_ducking.tool.duck_audio")
async def test_audio_ducking_tool_execution(mock_duck):
    """Verify tool delegates to logic and returns toon-encoded output."""
    from features.audio_ducking.models import AudioDuckingOutput, DuckingParams

    mcp = FastMCP("Test Server")
    register_audio_ducking(mcp)

    mock_duck.return_value = AudioDuckingOutput(
        output_path="mixed.wav",
        params=DuckingParams(threshold=0.1, ratio=5.0, attack=20, release=500),
    )

    result = await mcp.call_tool(
        "audio_ducking",
        {
            "voice_path": "voice.wav",
            "music_path": "music.mp3",
            "output_path": "mixed.wav",
        },
    )
    assert "mixed.wav" in result.content[0].text
    mock_duck.assert_called_once()
