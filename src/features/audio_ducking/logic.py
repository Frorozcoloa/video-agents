"""Logic for the audio ducking feature."""

import os
import ffmpeg
from .models import AudioDuckingInput, AudioDuckingOutput, DuckingParams


def duck_audio(request: AudioDuckingInput) -> AudioDuckingOutput:
    """
    Mix a voice track over background music with automatic sidechain ducking.

    Builds an FFmpeg filter graph:
      1. Normalise both inputs to stereo via aformat.
      2. asplit the voice into (sidechain trigger, voice passthrough).
      3. sidechaincompress the music track using the voice sidechain.
      4. amix the voice passthrough and the ducked music into one stereo output.

    Args:
        request: AudioDuckingInput with voice/music paths and compression params.

    Returns:
        AudioDuckingOutput with the output file path and applied params.

    Raises:
        FileNotFoundError: If voice or music file does not exist.
        NotADirectoryError: If the output directory does not exist.
        RuntimeError: If FFmpeg processing fails.
    """
    if not os.path.exists(request.voice_path):
        raise FileNotFoundError(f"Voice file not found: {request.voice_path}")
    if not os.path.exists(request.music_path):
        raise FileNotFoundError(f"Music file not found: {request.music_path}")

    output_dir = os.path.dirname(os.path.abspath(request.output_path))
    if not os.path.isdir(output_dir):
        raise NotADirectoryError(f"Output directory does not exist: {output_dir}")

    try:
        voice_in = ffmpeg.input(request.voice_path)
        music_in = ffmpeg.input(request.music_path)

        # Normalise both to stereo to avoid channel mismatch errors
        voice_stereo = voice_in.audio.filter("aformat", channel_layouts="stereo")
        music_stereo = music_in.audio.filter("aformat", channel_layouts="stereo")

        # Split voice: stream(0) → sidechain trigger, stream(1) → passthrough
        voice_split = voice_stereo.filter_multi_output("asplit", 2)
        sc_trigger = voice_split.stream(0)
        voice_pass = voice_split.stream(1)

        # Compress music using voice as sidechain trigger
        ducked_music = ffmpeg.filter(
            [music_stereo, sc_trigger],
            "sidechaincompress",
            threshold=request.threshold,
            ratio=request.ratio,
            attack=request.attack,
            release=request.release,
        )

        # Mix voice passthrough + ducked music
        mixed = ffmpeg.filter([voice_pass, ducked_music], "amix", inputs=2)

        (
            ffmpeg.output(mixed, request.output_path)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        return AudioDuckingOutput(
            output_path=request.output_path,
            params=DuckingParams(
                threshold=request.threshold,
                ratio=request.ratio,
                attack=request.attack,
                release=request.release,
            ),
        )

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"FFmpeg audio ducking failed: {error_msg}")
