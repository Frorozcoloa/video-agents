"""Logic for the video clipping feature using ffmpeg-python SDK with forced 0-timestamp reset."""

import os
import ffmpeg
from .models import ClippingRequest, ClippingResponse


def clip_video_logic(request: ClippingRequest) -> ClippingResponse:
    """
    Extracts a segment from a video file based on start and end timestamps.

    Args:
        request: ClippingRequest object containing the video path and timestamps

    Returns:
        ClippingResponse object containing the output video path and success status
    """
    if not os.path.exists(request.video_path):
        raise FileNotFoundError(f"Archivo no encontrado: {request.video_path}")

    # Convert milliseconds to float seconds for FFmpeg
    start_f = float(request.start_time) / 1000.0
    end_f = float(request.end_time) / 1000.0

    duration = end_f - start_f

    if duration <= 0:
        raise ValueError(
            "La duración debe ser positiva (el tiempo de inicio debe ser menor al de fin)."
        )

    output_path = request.output_video_path
    if not output_path:
        base, ext = os.path.splitext(request.video_path)
        output_path = f"{base}_clip_{request.mode}{ext}"

    try:
        if request.mode == "fast":
            (
                ffmpeg.input(request.video_path)
                .output(
                    output_path,
                    ss=start_f,
                    t=duration,
                    c="copy",
                    avoid_negative_ts="make_non_negative",
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        else:
            (
                ffmpeg.input(request.video_path, ss=start_f)
                .output(
                    output_path,
                    t=duration,
                    vcodec="libx264",
                    acodec="aac",
                    crf=18,
                    preset="veryfast",
                    avoid_negative_ts="make_non_negative",
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

        return ClippingResponse(video_path=output_path, success=True)

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"Error en FFmpeg: {error_msg}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado: {str(e)}")
