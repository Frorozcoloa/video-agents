## 1. Setup

- [x] 1.1 Add `faster-whisper`, `silero-vad`, and `onnxruntime` to the project dependencies using `uv add`.
- [x] 1.2 Create the new feature directory structure at `src/features/audio_transcription/`.
- [x] 1.3 Add a placeholder `logic.py` and `models.py` in the new directory.

## 2. Audio Processing & VAD

- [x] 2.1 Implement the Silero-VAD logic to segment audio files into speech chunks, filtering silences > 2 seconds.
- [x] 2.2 Create a utility to convert VAD segments into a format compatible with Whisper processing.

## 3. Transcription Core

- [x] 3.1 Implement the `faster-whisper` inference logic, loading the `base` model by default.
- [x] 3.2 Ensure `word_timestamps=True` is passed to the transcribe method.
- [x] 3.3 Map the Whisper output segments to the required JSON structure (`texto`, `tiempo_inicio`, `tiempo_fin`).

## 4. MCP Integration

- [x] 4.1 Define the `TranscriptionRequest` and `TranscriptionResponse` Pydantic models in `models.py`.
- [x] 4.2 Register the `transcribe_audio` tool in the MCP server within `tool.py`.
- [x] 4.3 Ensure the tool accepts a file path (from previous audio extraction) and returns the structured JSON.

## 5. Verification & Testing

- [x] 5.1 Create a unit test `tests/test_audio_transcription.py` to verify the VAD logic with a sample audio file.
- [x] 5.2 Create an integration test to run the full transcription pipeline on a known audio clip.
- [x] 5.3 Verify the precision of the output timestamps against the input audio.
