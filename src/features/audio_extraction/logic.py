import os
import ffmpeg
from .models import ExtractionRequest, ExtractionResponse


def extract_audio_logic(request: ExtractionRequest) -> ExtractionResponse:
    """
    Extracts high-quality audio from a video file using FFmpeg.
    """
    if not os.path.exists(request.video_path):
        raise FileNotFoundError(f"Input video file not found: {request.video_path}")

    # Generate output path if not provided
    output_path = request.output_audio_path
    if not output_path:
        base, _ = os.path.splitext(request.video_path)
        output_path = f"{base}.mp3"

    try:
        # Build the FFmpeg command
        # vn=None (No Video)
        # acodec='libmp3lame' (MP3 codec)
        # q=2 (VBR high quality)
        (
            ffmpeg.input(request.video_path)
            .output(output_path, vn=None, acodec="libmp3lame", q=2)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return ExtractionResponse(audio_path=output_path, success=True)
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"FFmpeg audio extraction failed: {error_msg}")
