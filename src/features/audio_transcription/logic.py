"""Logic for the audio transcription feature."""

from typing import List, Dict, Any
from faster_whisper import WhisperModel

# Cache models to avoid reloading on every request
_WHISPER_MODELS = {}


def get_whisper_model(model_size: str = "base") -> WhisperModel:
    """Load Whisper model
    Args:
        model_size: Size of the Whisper model to load.
    Returns:
        WhisperModel: Whisper model
    """
    global _WHISPER_MODELS
    if model_size not in _WHISPER_MODELS:
        # CTranslate2 / faster-whisper logic using CPU and int8 for efficiency
        _WHISPER_MODELS[model_size] = WhisperModel(
            model_size, device="cpu", compute_type="int8"
        )
    return _WHISPER_MODELS[model_size]


def transcribe_audio_logic(
    audio_path: str, model_size: str = "base", min_silence_duration_ms: int = 2000
) -> List[Dict[str, Any]]:
    """
    Task 3.1-3.3: Faster-whisper transcription with word timestamps and VAD filter.

    Args:
        audio_path: Path to the audio file.
        model_size: Size of the Whisper model to load.
        min_silence_duration_ms: Minimum duration of silence to consider as a segment boundary.

    Returns:
        List[Dict[str, Any]]: List of transcribed segments.
    """
    model = get_whisper_model(model_size)

    # Using the optimized vad_filter=True within transcribe for best alignment
    segments, _ = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=min_silence_duration_ms),
    )

    results = []
    for segment in segments:
        if segment.words:
            for word in segment.words:
                results.append(
                    {
                        "texto": word.word.strip(),
                        "tiempo_inicio": int(word.start * 1000),
                        "tiempo_fin": int(word.end * 1000),
                    }
                )
        else:
            # Fallback to segment if word timestamps are unavailable
            results.append(
                {
                    "texto": segment.text.strip(),
                    "tiempo_inicio": int(segment.start * 1000),
                    "tiempo_fin": int(segment.end * 1000),
                }
            )
    return results
