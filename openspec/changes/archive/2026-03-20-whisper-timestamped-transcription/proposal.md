## Why

To enable precise alignment of text with video content by extracting transcriptions with word-level timestamps. This is a critical step for automated video editing, searchable video archives, and high-quality subtitle generation.

## What Changes

- **Transcription Engine**: Integration of `faster-whisper` (CTranslate2) for high-performance audio-to-text conversion.
- **Timestamping**: Mandatory activation of `word_timestamps=True` to provide millisecond-level precision for every word.
- **Pre-processing (VAD)**: Implementation of Silero-VAD to filter out silences (> 2 seconds) and background noise before transcription, reducing hallucinations and processing time.
- **Structured Output**: The tool will return a JSON array of segments, each containing `texto`, `tiempo_inicio` (ms), and `tiempo_fin` (ms).

## Capabilities

### New Capabilities
- `audio-transcription`: Converts audio files to text with word-level timestamps using Whisper and VAD optimization.

### Modified Capabilities
- (None)

## Impact

- **Dependencies**: Addition of `faster-whisper`, `silero-vad`, and `onnxruntime` to the project.
- **Server**: A new MCP tool will be registered in the server to handle transcription requests.
- **Performance**: High memory/GPU utilization during transcription; requires CTranslate2 for optimization.
