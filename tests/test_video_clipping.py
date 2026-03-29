import pytest
from unittest.mock import patch, MagicMock
from features.video_clipping.logic import clip_video_logic
from features.video_clipping.models import ClippingRequest
import ffmpeg


def test_clip_video_file_not_found():
    """Verify that a FileNotFoundError is raised if the input video file does not exist."""
    request = ClippingRequest(
        video_path="non_existent.mp4", start_time=10000, end_time=20000
    )
    with pytest.raises(FileNotFoundError):
        clip_video_logic(request)


@patch("os.path.exists")
def test_clip_video_invalid_timestamp_range(mock_exists):
    """Verify that a ValueError is raised if start_time >= end_time."""
    mock_exists.return_value = True
    request = ClippingRequest(video_path="test.mp4", start_time=20000, end_time=10000)
    with pytest.raises(ValueError) as excinfo:
        clip_video_logic(request)
    assert "La duración debe ser positiva" in str(excinfo.value)


@patch("os.path.exists")
@patch("ffmpeg.input")
def test_clip_video_fast_mode_parameters(mock_ffmpeg_input, mock_exists):
    """Verify that Fast Mode uses ffmpeg-python correctly."""
    mock_exists.return_value = True

    # Mock the chain: ffmpeg.input().output().overwrite_output().run()
    mock_input_node = MagicMock()
    mock_output_node = MagicMock()
    mock_overwrite_node = MagicMock()

    mock_ffmpeg_input.return_value = mock_input_node
    mock_input_node.output.return_value = mock_output_node
    mock_output_node.overwrite_output.return_value = mock_overwrite_node
    mock_overwrite_node.run.return_value = (b"stdout", b"stderr")

    request = ClippingRequest(
        video_path="input.mp4",
        start_time=10500,
        end_time=20000,
        mode="fast",
        output_video_path="output_fast.mp4",
    )
    response = clip_video_logic(request)

    assert response.success is True
    assert response.video_path == "output_fast.mp4"

    # Verify the parameters passed to output
    mock_input_node.output.assert_called_once()
    args, kwargs = mock_input_node.output.call_args
    assert args[0] == "output_fast.mp4"
    assert kwargs["ss"] == 10.5
    assert kwargs["t"] == 9.5
    assert kwargs["c"] == "copy"


@patch("os.path.exists")
@patch("ffmpeg.input")
def test_clip_video_exact_mode_parameters(mock_ffmpeg_input, mock_exists):
    """Verify that Exact Mode uses ffmpeg-python with correct re-encoding arguments."""
    mock_exists.return_value = True

    # Mock the chain
    mock_input_node = MagicMock()
    mock_output_node = MagicMock()
    mock_overwrite_node = MagicMock()

    mock_ffmpeg_input.return_value = mock_input_node
    mock_input_node.output.return_value = mock_output_node
    mock_output_node.overwrite_output.return_value = mock_overwrite_node
    mock_overwrite_node.run.return_value = (b"stdout", b"stderr")

    request = ClippingRequest(
        video_path="input.mp4",
        start_time=60000,
        end_time=120000,
        mode="exact",
        output_video_path="output_exact.mp4",
    )
    response = clip_video_logic(request)

    assert response.success is True
    assert response.video_path == "output_exact.mp4"

    # Verify input was called with ss
    mock_ffmpeg_input.assert_called_once_with("input.mp4", ss=60.0)

    # Verify output parameters
    mock_input_node.output.assert_called_once()
    args, kwargs = mock_input_node.output.call_args
    assert args[0] == "output_exact.mp4"
    assert kwargs["t"] == 60.0
    assert kwargs["vcodec"] == "libx264"
    assert kwargs["acodec"] == "aac"
    assert kwargs["crf"] == 18
    assert kwargs["preset"] == "veryfast"


@patch("os.path.exists")
@patch("ffmpeg.input")
def test_clip_video_ffmpeg_error(mock_ffmpeg_input, mock_exists):
    """Verify that a RuntimeError is raised if FFmpeg fails."""
    mock_exists.return_value = True

    mock_input_node = MagicMock()
    mock_output_node = MagicMock()
    mock_overwrite_node = MagicMock()

    mock_ffmpeg_input.return_value = mock_input_node
    mock_input_node.output.return_value = mock_output_node
    mock_output_node.overwrite_output.return_value = mock_overwrite_node

    # ffmpeg.Error expects (cmd, stdout, stderr)
    mock_overwrite_node.run.side_effect = ffmpeg.Error(
        "ffmpeg", b"", b"clipping failed stderr"
    )

    request = ClippingRequest(video_path="test.mp4", start_time=0, end_time=10000)
    with pytest.raises(RuntimeError) as excinfo:
        clip_video_logic(request)

    assert "Error en FFmpeg" in str(excinfo.value)
    assert "clipping failed stderr" in str(excinfo.value)


@patch("os.path.exists")
@patch("ffmpeg.input")
def test_clip_video_default_output_path(mock_ffmpeg_input, mock_exists):
    """Verify that a default output path is generated if not provided."""
    mock_exists.return_value = True

    mock_input_node = MagicMock()
    mock_output_node = MagicMock()
    mock_overwrite_node = MagicMock()

    mock_ffmpeg_input.return_value = mock_input_node
    mock_input_node.output.return_value = mock_output_node
    mock_output_node.overwrite_output.return_value = mock_overwrite_node
    mock_overwrite_node.run.return_value = (b"stdout", b"stderr")

    request = ClippingRequest(
        video_path="input.mp4", start_time=0, end_time=10000, mode="exact"
    )
    response = clip_video_logic(request)

    assert response.success is True
    assert response.video_path == "input_clip_exact.mp4"
