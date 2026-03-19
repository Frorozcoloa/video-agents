from unittest.mock import patch, MagicMock
from features.audio_transcription.logic import transcribe_audio_logic, get_whisper_model


@patch("features.audio_transcription.logic.WhisperModel")
def test_get_whisper_model_caching(mock_whisper_model):
    """Verify that get_whisper_model caches the model instance."""
    from features.audio_transcription import logic

    logic._WHISPER_MODELS = {}  # Reset cache

    model1 = get_whisper_model("tiny")
    model2 = get_whisper_model("tiny")

    assert model1 is model2
    mock_whisper_model.assert_called_once()


@patch("features.audio_transcription.logic.get_whisper_model")
def test_transcribe_audio_logic_fallback(mock_get_whisper_model):
    """Verify fallback to segment text if word-level timestamps are missing."""
    mock_model = MagicMock()
    mock_get_whisper_model.return_value = mock_model

    mock_segment = MagicMock()
    mock_segment.words = None
    mock_segment.text = " hello world "
    mock_segment.start = 1.0
    mock_segment.end = 2.5

    mock_model.transcribe.return_value = ([mock_segment], MagicMock())

    results = transcribe_audio_logic("dummy.wav")

    assert len(results) == 1
    assert results[0]["texto"] == "hello world"
    assert results[0]["tiempo_inicio"] == 1000
    assert results[0]["tiempo_fin"] == 2500


@patch("features.audio_transcription.logic.get_whisper_model")
def test_transcribe_audio_logic(mock_get_whisper_model):
    """Verify that transcription results are correctly mapped to the expected structure."""
    mock_model = MagicMock()
    mock_get_whisper_model.return_value = mock_model

    # Mock Whisper segments
    mock_word = MagicMock()
    mock_word.word = " hello"
    mock_word.start = 0.5
    mock_word.end = 1.0

    mock_segment = MagicMock()
    mock_segment.words = [mock_word]
    mock_segment.text = " hello"
    mock_segment.start = 0.5
    mock_segment.end = 1.0

    mock_model.transcribe.return_value = ([mock_segment], MagicMock())

    results = transcribe_audio_logic("dummy.wav")

    assert len(results) == 1
    assert results[0]["texto"] == "hello"
    assert results[0]["tiempo_inicio"] == 500
    assert results[0]["tiempo_fin"] == 1000

    # Verify model call parameters
    mock_model.transcribe.assert_called_once()
    _, kwargs = mock_model.transcribe.call_args
    assert kwargs["word_timestamps"] is True
    assert kwargs["vad_filter"] is True
