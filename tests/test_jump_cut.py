import pytest
from unittest.mock import patch, MagicMock
from features.video_clipping.models import JumpCutRequest
from features.video_clipping.logic import process_jump_cut
from features.video_clipping.utils import (
    prepare_audio_for_vad,
    detect_speech,
    apply_ffmpeg_jump_cut,
)


@patch("os.path.exists")
def test_jump_cut_file_not_found(mock_exists):
    """Ensure FileNotFoundError is raised if video doesn't exist."""
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        process_jump_cut(
            JumpCutRequest(video_path="non_existent.mp4", audio_path="audio.mp3")
        )


@patch("os.path.exists")
@patch("os.remove")
@patch("features.video_clipping.logic.prepare_audio_for_vad")
@patch("features.video_clipping.logic.detect_speech")
@patch("features.video_clipping.logic.apply_ffmpeg_jump_cut")
def test_process_jump_cut_success(
    mock_apply_ffmpeg, mock_detect_speech, mock_extract_audio, mock_remove, mock_exists
):
    """Test the orchestration function."""
    mock_exists.return_value = True
    mock_extract_audio.return_value = "temp.wav"
    mock_detect_speech.return_value = [{"start": 1000, "end": 2000}]
    mock_apply_ffmpeg.return_value = "output.mp4"

    request = JumpCutRequest(
        video_path="input.mp4", audio_path="audio.mp3", output_video_path="output.mp4"
    )
    response = process_jump_cut(request)

    assert response.success is True
    assert response.video_path == "output.mp4"
    assert response.cut_count == 1

    mock_extract_audio.assert_called_once_with("audio.mp3")
    mock_detect_speech.assert_called_once_with("temp.wav")
    mock_apply_ffmpeg.assert_called_once_with(
        "input.mp4", "output.mp4", [{"start": 1000, "end": 2000}]
    )
    mock_remove.assert_called_once_with("temp.wav")


@patch("features.video_clipping.utils.NamedTemporaryFile")
@patch("ffmpeg.input")
def test_prepare_audio_for_vad(mock_ffmpeg_input, mock_named_temp):
    """Test standard ffmpeg fallback for audio extraction."""
    mock_temp = MagicMock()
    mock_temp.name = "temp_audio.wav"
    mock_named_temp.return_value.__enter__.return_value = mock_temp

    mock_input_node = MagicMock()
    mock_input_node.output.return_value.overwrite_output.return_value.run.return_value = (
        b"",
        b"",
    )
    mock_ffmpeg_input.return_value = mock_input_node

    result = prepare_audio_for_vad("audio.mp3")
    assert result == "temp_audio.wav"


@patch("features.video_clipping.utils.load_silero_vad")
@patch("features.video_clipping.utils.read_audio")
@patch("features.video_clipping.utils.get_speech_timestamps")
def test_detect_speech_no_voice(mock_get_timestamps, mock_read_audio, mock_load_vad):
    mock_load_vad.return_value = "model"
    mock_read_audio.return_value = "wav"
    mock_get_timestamps.return_value = []

    with pytest.raises(ValueError, match="No se detectó voz en el audio proporcionado"):
        detect_speech("audio.wav")


@patch("ffmpeg.input")
@patch("ffmpeg.output")
def test_apply_ffmpeg_jump_cut(mock_ffmpeg_output, mock_ffmpeg_input):
    mock_input_node = MagicMock()
    mock_ffmpeg_input.return_value = mock_input_node

    mock_v_filter = MagicMock()
    mock_a_filter = MagicMock()
    mock_input_node.video.filter.return_value.filter.return_value = mock_v_filter
    mock_input_node.audio.filter.return_value.filter.return_value = mock_a_filter

    mock_output_node = MagicMock()
    mock_output_node.overwrite_output.return_value.run.return_value = (b"", b"")
    mock_ffmpeg_output.return_value = mock_output_node

    timestamps = [{"start": 1123, "end": 4567}]
    result = apply_ffmpeg_jump_cut("input.mp4", "out.mp4", timestamps)

    assert result == "out.mp4"
    mock_ffmpeg_output.assert_called_once()
