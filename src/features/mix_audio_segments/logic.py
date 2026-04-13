"""Logic for the mix audio segments feature."""

import os
import ffmpeg
from .models import MixAudioSegmentsInput, MixAudioSegmentsOutput


def mix_audio_segments_logic(request: MixAudioSegmentsInput) -> MixAudioSegmentsOutput:
    """
    Layer timed audio segments over the original audio track of a video.

    Builds an FFmpeg filter graph that:
    1. Optionally includes the original video audio as the base stream
       (skipped when replace_original=True).
    2. For each segment: loads its audio, trims it to the declared duration,
       and delays it to its start position.
    3. Mixes all streams with amix normalize=0.
    4. Outputs the new audio alongside the copied video stream.

    Args:
        request: MixAudioSegmentsInput with video path, segments, and output path.

    Returns:
        MixAudioSegmentsOutput with output path and segment count.

    Raises:
        FileNotFoundError: If the video or any segment audio file does not exist.
        NotADirectoryError: If the output directory does not exist.
        RuntimeError: If FFmpeg processing fails.
    """
    if not os.path.exists(request.video_path):
        raise FileNotFoundError(f"Video file not found: {request.video_path}")

    for seg in request.segments:
        if not os.path.exists(seg.audio_path):
            raise FileNotFoundError(f"Segment audio file not found: {seg.audio_path}")

    output_path = request.output_path
    if not output_path:
        base, ext = os.path.splitext(request.video_path)
        output_path = f"{base}_mixed{ext}"

    output_dir = os.path.dirname(os.path.abspath(output_path))
    if not os.path.isdir(output_dir):
        raise NotADirectoryError(f"Output directory does not exist: {output_dir}")

    try:
        video_in = ffmpeg.input(request.video_path)

        segment_streams = []
        for seg in request.segments:
            duration_s = (seg.end_ms - seg.start_ms) / 1000.0
            audio_in = ffmpeg.input(seg.audio_path)
            trimmed = audio_in.audio.filter("atrim", duration=duration_s)
            delayed = trimmed.filter("adelay", f"{seg.start_ms}|{seg.start_ms}")
            segment_streams.append(delayed)

        if request.replace_original:
            all_streams = segment_streams
        else:
            all_streams = [video_in.audio] + segment_streams

        mixed = ffmpeg.filter(all_streams, "amix", inputs=len(all_streams), normalize=0)

        (
            ffmpeg.output(video_in.video, mixed, output_path, vcodec="copy")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        return MixAudioSegmentsOutput(
            output_path=output_path,
            segments_count=len(request.segments),
        )

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"FFmpeg mix audio segments failed: {error_msg}")
