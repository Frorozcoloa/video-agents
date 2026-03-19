## Context

The `video-agents` project currently has capabilities for video processing and audio extraction. This change adds the next step in the pipeline: converting the extracted audio into a machine-readable transcription with high temporal precision. We use `faster-whisper` to ensure this is performant enough for local execution.

## Goals / Non-Goals

**Goals:**
- Implement a robust transcription tool using `faster-whisper`.
- Ensure millisecond precision for every word using `word_timestamps=True`.
- Reduce noise and hallucinations by integrating Silero-VAD for silence detection.
- Provide a standardized JSON output format for downstream LLM processing.

**Non-Goals:**
- Implementing real-time (streaming) transcription.
- Building a custom UI for transcription review (CLI/API only).
- Supporting every Whisper model size (defaulting to `base` for efficiency, configurable to `small/medium`).

## Decisions

- **Inference Engine**: Use `faster-whisper` with CTranslate2 backend. This provides a significant performance boost (up to 4x faster) compared to the standard `openai-whisper` while using less VRAM.
- **VAD Pre-processing**: Integrate `silero-vad` via `onnxruntime`. This will segment the audio and only process portions containing speech, filtering out silences longer than 2 seconds. This prevents the model from "hallucinating" text during long periods of silence.
- **Data Model**: The output will be a list of segment objects.
  ```json
  [
    {
      "texto": "Hello world",
      "tiempo_inicio": 1200,
      "tiempo_fin": 2500
    }
  ]
  ```
- **Concurrency**: Transcription is a CPU/GPU intensive task. The tool will handle requests sequentially or with a small, configurable pool to avoid system exhaustion.

## Risks / Trade-offs

- **Memory Consumption**: Even with `faster-whisper`, loading the model and processing audio requires significant memory.
  - *Mitigation*: Use `compute_type="int8"` or `compute_type="float16"` depending on hardware availability to reduce footprint.
- **Model Download**: Models need to be downloaded on the first run.
  - *Mitigation*: Ensure the implementation handles model caching correctly and provides feedback during the initial download.
- **Accuracy on Overlapping Speech**: Whisper can struggle when multiple people speak at once.
  - *Mitigation*: While VAD helps with silences, diarization is out of scope for this initial implementation.
