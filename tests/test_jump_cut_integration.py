"""
Integration test for the jump cut feature with real audio-video sync verification.

This test uses real media files to verify that jump cuts maintain audio-video
synchronization. It requires `tmp/testing.mp4` to exist in the project root.

Run with:
    uv run pytest tests/test_jump_cut_integration.py -v -s

To exclude from CI (fast unit tests only), skip with:
    uv run pytest -m "not integration"
"""

import json
import os
import subprocess

import pytest

from features.video_clipping.logic import process_jump_cut
from features.video_clipping.models import JumpCutRequest

# Path to the source test video (relative to project root)
SOURCE_VIDEO = "tmp/testing.mp4"


def _probe_streams(video_path: str) -> dict:
    """
    Run ffprobe on a video file and return stream info as a dict with
    'video' and 'audio' keys, each containing the first matching stream.
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"ffprobe failed: {result.stderr}"
    data = json.loads(result.stdout)
    streams = data.get("streams", [])

    info = {}
    for s in streams:
        codec_type = s.get("codec_type", "")
        if codec_type == "video" and "video" not in info:
            info["video"] = s
        elif codec_type == "audio" and "audio" not in info:
            info["audio"] = s

    return info


@pytest.mark.integration
@pytest.mark.slow
class TestJumpCutIntegration:
    """Integration tests for jump cut audio-video sync verification."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup test files and cleanup after each test."""
        self.input_video = "/tmp/test_jumpcut_input.mp4"
        self.input_audio = "/tmp/test_jumpcut_audio.mp3"
        self.output_video = "/tmp/test_jumpcut_output.mp4"

        # Skip entire class if source video is missing
        if not os.path.exists(SOURCE_VIDEO):
            pytest.skip(
                f"Source video '{SOURCE_VIDEO}' not found. Skipping integration tests."
            )

        # Copy only the first 30 seconds to keep the test fast
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                SOURCE_VIDEO,
                "-t",
                "30",  # Only first 30 seconds
                "-c",
                "copy",
                self.input_video,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Failed to copy source video: {result.stderr}"

        # Extract audio from the clipped input
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                self.input_video,
                "-vn",
                "-acodec",
                "libmp3lame",
                "-q:a",
                "2",
                self.input_audio,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Failed to extract audio: {result.stderr}"

        yield

        # Cleanup all temp files after the test
        for f in [self.input_video, self.input_audio, self.output_video]:
            if os.path.exists(f):
                os.remove(f)

    def test_jump_cut_output_file_is_created(self):
        """Verify that process_jump_cut creates an output video file."""
        request = JumpCutRequest(
            video_path=self.input_video,
            audio_path=self.input_audio,
            output_video_path=self.output_video,
        )
        response = process_jump_cut(request)

        assert response.success is True, "process_jump_cut reported failure"
        assert os.path.exists(self.output_video), (
            f"Output video not found at {self.output_video}"
        )
        assert os.path.getsize(self.output_video) > 0, "Output video is empty"

    def test_jump_cut_output_has_both_streams(self):
        """Verify the output video contains both video and audio streams."""
        request = JumpCutRequest(
            video_path=self.input_video,
            audio_path=self.input_audio,
            output_video_path=self.output_video,
        )
        process_jump_cut(request)

        streams = _probe_streams(self.output_video)

        assert "video" in streams, "Output video is missing a video stream"
        assert "audio" in streams, "Output video is missing an audio stream"

    def test_jump_cut_audio_video_sync(self):
        """
        Core sync test: audio and video durations must match within 0.1s
        and both streams must start at timestamp 0 (no drift).
        """
        request = JumpCutRequest(
            video_path=self.input_video,
            audio_path=self.input_audio,
            output_video_path=self.output_video,
        )
        response = process_jump_cut(request)

        assert response.success is True

        streams = _probe_streams(self.output_video)
        video_stream = streams["video"]
        audio_stream = streams["audio"]

        # --- Duration sync check ---
        assert "duration" in video_stream, "Video stream is missing 'duration' metadata"
        assert "duration" in audio_stream, "Audio stream is missing 'duration' metadata"

        video_duration = float(video_stream["duration"])
        audio_duration = float(audio_stream["duration"])

        duration_diff = abs(video_duration - audio_duration)
        assert duration_diff < 0.1, (
            f"Audio-video duration mismatch! "
            f"video={video_duration:.3f}s, audio={audio_duration:.3f}s, "
            f"diff={duration_diff:.3f}s (tolerance: 0.1s)"
        )

        # --- Start time / PTS drift check ---
        video_start = float(video_stream.get("start_time", 0))
        audio_start = float(audio_stream.get("start_time", 0))

        assert video_start == pytest.approx(0.0, abs=0.01), (
            f"Video stream does not start at 0 (start_time={video_start}s). "
            "Possible PTS drift detected."
        )
        assert audio_start == pytest.approx(0.0, abs=0.01), (
            f"Audio stream does not start at 0 (start_time={audio_start}s). "
            "Possible PTS drift detected."
        )

    def test_jump_cut_cut_count_is_positive(self):
        """Verify that at least one voice segment was detected and cut."""
        request = JumpCutRequest(
            video_path=self.input_video,
            audio_path=self.input_audio,
            output_video_path=self.output_video,
        )
        response = process_jump_cut(request)

        assert response.cut_count > 0, (
            "Expected at least one voice segment to be detected, "
            f"but got cut_count={response.cut_count}"
        )

    def test_jump_cut_output_shorter_than_input(self):
        """Verify that jump cuts actually removed silence (output < input)."""
        request = JumpCutRequest(
            video_path=self.input_video,
            audio_path=self.input_audio,
            output_video_path=self.output_video,
        )
        process_jump_cut(request)

        input_streams = _probe_streams(self.input_video)
        output_streams = _probe_streams(self.output_video)

        input_duration = float(input_streams["video"]["duration"])
        output_duration = float(output_streams["video"]["duration"])

        assert output_duration < input_duration, (
            f"Jump cut output ({output_duration:.2f}s) is not shorter than "
            f"input ({input_duration:.2f}s). Silence may not have been removed."
        )
