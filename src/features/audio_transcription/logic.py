"""Logic for the audio transcription feature."""

from faster_whisper import WhisperModel
from toon_format import encode
from functools import lru_cache


@lru_cache(maxsize=None)
def get_whisper_model(model_size: str = "base") -> WhisperModel:
    """Load Whisper model
    Args:
        model_size: Size of the Whisper model to load.
    Returns:
        WhisperModel: Whisper model
    """
    # CTranslate2 / faster-whisper logic using CPU and int8 for efficiency
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe_audio_logic(
    audio_path: str,
    model_size: str = "base",
    min_silence_duration_ms: int = 2000,
) -> str:
    """
    Transcribe audio with Faster-whisper, word timestamps and VAD filter.
    Returns the transcription in TOON (Token-Oriented Object Notation) format.

    Args:
        audio_path: Path to the audio file.
        model_size: Size of the Whisper model to load.
        min_silence_duration_ms: Minimum duration of silence to consider as a segment boundary.

    Returns:
        str: Transcription in TOON format.
    """
    model = get_whisper_model(model_size)
    segments_gen, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=min_silence_duration_ms),
    )

    results = []
    for segment in segments_gen:
        if segment.words:
            for word in segment.words:
                results.append(
                    {
                        "text": word.word.strip(),
                        "start": int(word.start * 1000),
                        "end": int(word.end * 1000),
                    }
                )
        else:
            # Fallback to segment if word timestamps are unavailable
            results.append(
                {
                    "text": segment.text.strip(),
                    "start": int(segment.start * 1000),
                    "end": int(segment.end * 1000),
                }
            )

    # Return encoded TOON string
    return encode({"transcription": results})
