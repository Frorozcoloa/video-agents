import pytest
from unittest.mock import patch, MagicMock
from features.audio_extraction.logic import extract_audio_logic
from features.audio_extraction.models import ExtractionRequest


def test_extract_audio_file_not_found():
    """Verify that a FileNotFoundError is raised if the input file does not exist."""
    request = ExtractionRequest(video_path="non_existent_video.mp4")
    with pytest.raises(FileNotFoundError):
        extract_audio_logic(request)


@patch("os.path.exists")
@patch("ffmpeg.input")
def test_extract_audio_logic_parameters(mock_ffmpeg_input, mock_exists):
    """
    Verify that FFmpeg is called with the correct parameters:
    vn=None, acodec='libmp3lame', q=2.
    """
    mock_exists.return_value = True

    # Setup mock chain for ffmpeg
    # ffmpeg.input().output().overwrite_output().run()
    mock_output = MagicMock()
    mock_overwrite = MagicMock()

    mock_ffmpeg_input.return_value.output.return_value = mock_output
    mock_output.overwrite_output.return_value = mock_overwrite
    mock_overwrite.run.return_value = (b"stdout", b"stderr")

    request = ExtractionRequest(
        video_path="test_video.mp4", output_audio_path="test_audio.mp3"
    )
    response = extract_audio_logic(request)

    # Assertions
    assert response.success is True
    assert response.audio_path == "test_audio.mp3"

    # Verify ffmpeg.input was called with the correct path
    mock_ffmpeg_input.assert_called_once_with("test_video.mp4")

    # Verify .output was called with correct parameters
    mock_ffmpeg_input.return_value.output.assert_called_once_with(
        "test_audio.mp3", vn=None, acodec="libmp3lame", q=2
    )

    # Verify .run was called
    mock_overwrite.run.assert_called_once()


@patch("os.path.exists")
@patch("ffmpeg.input")
def test_extract_audio_default_output_path(mock_ffmpeg_input, mock_exists):
    """Verify that the default output path is generated correctly if not provided."""
    mock_exists.return_value = True

    mock_output = MagicMock()
    mock_overwrite = MagicMock()
    mock_ffmpeg_input.return_value.output.return_value = mock_output
    mock_output.overwrite_output.return_value = mock_overwrite
    mock_overwrite.run.return_value = (b"stdout", b"stderr")

    request = ExtractionRequest(video_path="my_video.mp4")
    response = extract_audio_logic(request)

    assert response.audio_path == "my_video.mp3"
    mock_ffmpeg_input.return_value.output.assert_called_once_with(
        "my_video.mp3", vn=None, acodec="libmp3lame", q=2
    )
