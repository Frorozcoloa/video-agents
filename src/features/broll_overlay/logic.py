"""Logic for the B-roll overlay feature using FFmpeg complex filter graph."""

import os
import ffmpeg
from .models import BrollRequest


def apply_broll(request: BrollRequest) -> str:
    """
    Overlay a B-roll clip onto a time-bounded segment of the main video.

    Builds an FFmpeg complex filter graph that:
    1. Splits the main video stream for dual use.
    2. Trims a segment from the main video.
    3. Scales the B-roll to match the main video dimensions.
    4. Overlays the B-roll on the segment with eof_action=repeat (freeze last
       frame when B-roll is shorter than the segment).
    5. Composites the overlaid segment back onto the main video.
    Main audio is preserved; B-roll audio is discarded.

    Args:
        request: BrollRequest with paths, timestamps, and optional output path.

    Returns:
        str: Path to the output video file.

    Raises:
        FileNotFoundError: If the main video or B-roll file does not exist.
        RuntimeError: If FFmpeg fails during processing.
    """
    if not os.path.exists(request.video_path):
        raise FileNotFoundError(f"Video not found: {request.video_path}")
    if not os.path.exists(request.broll_path):
        raise FileNotFoundError(f"B-roll not found: {request.broll_path}")

    probe = ffmpeg.probe(request.video_path)
    video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    width = video_stream["width"]
    height = video_stream["height"]

    start_s = request.start_ms / 1000.0
    end_s = request.end_ms / 1000.0

    output_path = request.output_path
    if not output_path:
        base, ext = os.path.splitext(request.video_path)
        output_path = f"{base}_broll{ext}"

    try:
        main_input = ffmpeg.input(request.video_path)
        broll_input = ffmpeg.input(request.broll_path)

        # Split main video stream — referenced twice (trim + final composite)
        split = main_input.video.filter_multi_output("split", 2)
        main_v1 = split.stream(0)
        main_v2 = split.stream(1)

        # Extract segment and reset presentation timestamps
        segment = main_v1.trim(start=start_s, end=end_s).filter(
            "setpts", "PTS-STARTPTS"
        )

        # Scale B-roll to match main video dimensions
        broll_scaled = broll_input.video.filter("scale", width, height)

        # Overlay B-roll on segment; repeat last frame when B-roll is shorter
        overlaid = ffmpeg.filter(
            [segment, broll_scaled], "overlay", eof_action="repeat"
        )

        # Composite overlaid segment back onto the full main video at the right time
        out_video = ffmpeg.filter(
            [main_v2, overlaid],
            "overlay",
            enable=f"between(t,{start_s},{end_s})",
        )

        (
            ffmpeg.output(out_video, main_input.audio, output_path)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        return output_path

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"FFmpeg error: {error_msg}")
