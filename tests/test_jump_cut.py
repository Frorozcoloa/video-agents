import pytest
from unittest.mock import patch, MagicMock
import numpy as np
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
@patch("features.video_clipping.utils.sf.read")
@patch("features.video_clipping.utils.get_speech_timestamps")
def test_detect_speech_no_voice(mock_get_timestamps, mock_sf_read, mock_load_vad):
    mock_load_vad.return_value = "model"
    mock_sf_read.return_value = (
        np.zeros(1000, dtype=np.float32),
        16000,
    )  # Mock audio data and sample rate
    mock_get_timestamps.return_value = []

    with pytest.raises(ValueError, match="No se detectó voz en el audio proporcionado"):
        detect_speech("audio.wav")


@patch("features.video_clipping.utils.subprocess.run")
def test_apply_ffmpeg_jump_cut(mock_run):
    """Test that apply_ffmpeg_jump_cut calls subprocess with a valid ffmpeg command."""
    mock_run.return_value = MagicMock(returncode=0)

    timestamps = [{"start": 1123, "end": 4567}]
    result = apply_ffmpeg_jump_cut("input.mp4", "out.mp4", timestamps)

    assert result == "out.mp4"
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "ffmpeg"
    assert "out.mp4" in cmd


@patch("features.video_clipping.utils.subprocess.run")
def test_apply_ffmpeg_jump_cut_sync_parameters(mock_run):
    """Test that the concat-filter approach is used for perfect A/V sync.

    The concat filter approach (multiple -ss/-to inputs joined with concat=n=N:v=1:a=1)
    achieves 0.000s audio-video duration mismatch, unlike select/aselect which has a
    residual ~0.13s drift due to frame-boundary vs sample-boundary rounding differences.
    """
    mock_run.return_value = MagicMock(returncode=0)

    timestamps = [{"start": 1000, "end": 2000}, {"start": 3000, "end": 5000}]
    apply_ffmpeg_jump_cut("input.mp4", "out.mp4", timestamps)

    cmd = mock_run.call_args[0][0]
    cmd_str = " ".join(cmd)

    # Verify the concat filter is used (not select/aselect)
    assert "concat" in cmd_str, "concat filter must be present for perfect A/V sync"
    assert "filter_complex" in cmd_str, "-filter_complex flag must be present"
    assert "n=2" in cmd_str, "concat must reference 2 segments"

    # Verify both stream outputs are mapped
    assert "[outv]" in cmd_str, "video output stream [outv] must be mapped"
    assert "[outa]" in cmd_str, "audio output stream [outa] must be mapped"

    # Verify codec settings are present
    assert "libx264" in cmd_str
    assert "aac" in cmd_str


@patch("features.video_clipping.utils.load_silero_vad")
@patch("features.video_clipping.utils.sf.read")
@patch("features.video_clipping.utils.get_speech_timestamps")
def test_detect_speech_success(mock_get_timestamps, mock_sf_read, mock_load_vad):
    """Test that detect_speech converts seconds to milliseconds correctly."""
    mock_load_vad.return_value = "model"
    mock_sf_read.return_value = (
        np.zeros(1000, dtype=np.float32),
        16000,
    )  # Mock audio data and sample rate
    mock_get_timestamps.return_value = [
        {"start": 1.5, "end": 3.0},
        {"start": 5.0, "end": 7.25},
    ]

    result = detect_speech("audio.wav")

    assert result == [{"start": 1500, "end": 3000}, {"start": 5000, "end": 7250}]


@patch("features.video_clipping.utils.NamedTemporaryFile")
@patch("ffmpeg.input")
def test_prepare_audio_for_vad_ffmpeg_error(mock_ffmpeg_input, mock_named_temp):
    """Test that ffmpeg errors in prepare_audio_for_vad raise RuntimeError."""
    import ffmpeg

    mock_temp = MagicMock()
    mock_temp.name = "temp_audio.wav"
    mock_named_temp.return_value.__enter__.return_value = mock_temp

    mock_input_node = MagicMock()
    mock_ffmpeg_input.return_value = mock_input_node
    mock_input_node.output.return_value.overwrite_output.return_value.run.side_effect = ffmpeg.Error(
        "ffmpeg", b"", b"audio conversion failed"
    )

    with pytest.raises(RuntimeError, match="Error extracting/preparing audio"):
        prepare_audio_for_vad("bad_audio.mp3")


@patch("features.video_clipping.utils.subprocess.run")
def test_apply_ffmpeg_jump_cut_ffmpeg_error(mock_run):
    """Test that a non-zero ffmpeg exit code raises RuntimeError."""
    mock_run.return_value = MagicMock(
        returncode=1,
        stderr=b"filter error",
    )

    with pytest.raises(RuntimeError, match="Error applying jump cuts"):
        apply_ffmpeg_jump_cut("input.mp4", "out.mp4", [{"start": 1000, "end": 2000}])


def test_apply_ffmpeg_jump_cut_empty_timestamps():
    """Test that an empty timestamps list raises ValueError."""
    with pytest.raises(ValueError, match="timestamps list is empty"):
        apply_ffmpeg_jump_cut("input.mp4", "out.mp4", [])


@patch("os.path.exists")
@patch("features.video_clipping.logic.prepare_audio_for_vad")
def test_process_jump_cut_generic_exception(mock_extract_audio, mock_exists):
    """Test that unexpected errors in process_jump_cut are wrapped in RuntimeError."""
    mock_exists.return_value = True
    mock_extract_audio.side_effect = Exception("unexpected error")

    request = JumpCutRequest(
        video_path="input.mp4", audio_path="audio.mp3", output_video_path="output.mp4"
    )
    with pytest.raises(RuntimeError, match="Error procesando jump cut"):
        process_jump_cut(request)
