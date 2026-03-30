"""Utility functions for the video clipping feature."""

import os
import subprocess
from tempfile import NamedTemporaryFile
import ffmpeg

try:
    from silero_vad import load_silero_vad, get_speech_timestamps
    import torch
    import soundfile as sf
except ImportError as e:
    raise ImportError(
        "silero-vad, torch, and soundfile are required for VAD-based jump cuts."
    ) from e


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
    audio_np, sr = sf.read(audio_path, dtype="float32")
    wav = torch.from_numpy(audio_np)
    if wav.dim() > 1:
        wav = wav.mean(dim=-1)
    timestamps = get_speech_timestamps(
        wav, model, sampling_rate=sr, return_seconds=True
    )
    if not timestamps:
        raise ValueError("No se detectó voz en el audio proporcionado.")

    return [
        {"start": int(t["start"] * 1000), "end": int(t["end"] * 1000)}
        for t in timestamps
    ]


def apply_ffmpeg_jump_cut(video_path: str, output_path: str, timestamps: list) -> str:
    """Creates a jump cut video by concatenating speech segments using FFmpeg.

    Each speech segment is opened as a separate trimmed input, then all segments are
    joined with the ``concat`` filter. This approach achieves perfect audio-video sync
    (0.000s duration mismatch) because the muxer receives contiguous streams with
    consistent timestamps — unlike the ``select``/``aselect`` approach which can leave a
    small drift between video-frame-boundary rounding (1/fps) and audio-frame-boundary
    rounding (samples/sample_rate).
    """
    if not timestamps:
        raise ValueError("timestamps list is empty — no segments to concatenate.")

    n = len(timestamps)

    # Build the ffmpeg command manually.
    # ffmpeg-python does not cleanly support multi-input filter_complex with explicit
    # -map for each output stream, so we build the command as a list for subprocess.
    cmd = ["ffmpeg", "-y"]

    # One input per speech segment (seek with -ss/-to before decoding = fast)
    for segment in timestamps:
        start_sec = round(segment["start"] / 1000.0, 3)
        end_sec = round(segment["end"] / 1000.0, 3)
        cmd += ["-ss", str(start_sec), "-to", str(end_sec), "-i", video_path]

    # filter_complex: join all [i:v][i:a] pairs with the concat filter
    stream_pairs = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    concat_expr = f"{stream_pairs}concat=n={n}:v=1:a=1[outv][outa]"
    cmd += ["-filter_complex", concat_expr]

    # Map the named outputs and set codecs
    cmd += [
        "-map",
        "[outv]",
        "-map",
        "[outa]",
        "-vcodec",
        "libx264",
        "-acodec",
        "aac",
        "-crf",
        "18",
        "-preset",
        "veryfast",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        error_msg = result.stderr.decode(errors="replace")
        raise RuntimeError(f"Error applying jump cuts con FFmpeg: {error_msg}")

    return output_path
