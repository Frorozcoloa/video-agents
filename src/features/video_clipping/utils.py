"""Utility functions for the video clipping feature."""

import os
from tempfile import NamedTemporaryFile
import ffmpeg

try:
    from silero_vad import load_silero_vad, get_speech_timestamps, read_audio
except ImportError:
    pass


def prepare_audio_for_vad(input_audio_path: str) -> str:
    """Converts the input audio to 16kHz mono audio for VAD processing."""
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        temp_audio = temp_audio_file.name

    try:
        (
            ffmpeg.input(input_audio_path)
            .output(temp_audio, ac=1, ar=16000, format="wav")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return temp_audio
    except ffmpeg.Error as e:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"Error extracting/preparing audio: {error_msg}")


def detect_speech(audio_path: str) -> list:
    """Uses Silero VAD to detect speech segments, returning timestamps in milliseconds."""
    model = load_silero_vad()
    wav = read_audio(audio_path)
    timestamps = get_speech_timestamps(wav, model, return_seconds=True)
    if not timestamps:
        raise ValueError("No se detectó voz en el audio proporcionado.")

    return [
        {"start": int(t["start"] * 1000), "end": int(t["end"] * 1000)}
        for t in timestamps
    ]


def apply_ffmpeg_jump_cut(video_path: str, output_path: str, timestamps: list) -> str:
    """Creates a jump cut video using FFmpeg filters based on speech timestamps (in ms)."""
    select_exprs = []
    for segment in timestamps:
        start_sec = round(segment["start"] / 1000.0, 3)
        end_sec = round(segment["end"] / 1000.0, 3)
        select_exprs.append(f"between(t,{start_sec},{end_sec})")

    select_str = "+".join(select_exprs)

    inp = ffmpeg.input(video_path)
    v = inp.video.filter("select", select_str).filter("setpts", "N/FRAME_RATE/TB")
    a = inp.audio.filter("aselect", select_str).filter("asetpts", "N/SR/TB")

    try:
        (
            ffmpeg.output(
                v,
                a,
                output_path,
                vcodec="libx264",
                acodec="aac",
                crf=18,
                preset="veryfast",
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"Error applying jump cuts con FFmpeg: {error_msg}")
