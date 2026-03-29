## Why

The current audio transcription tool returns a standard JSON format, which can be verbose and consume a high number of tokens in model responses. Transitioning to the Toon protocol (via `toon-format`) provides a more compact, structured, and standardized way to represent temporal media data. This reduces token overhead for LLMs and improves interoperability within the AI-driven video editing pipeline.

## What Changes

- **BREAKING**: Modify the audio transcription tool to return data using the Toon protocol instead of the current JSON format.
- Add `toon-format` as a project dependency.
- Update the transcription logic to map `faster-whisper` segments to Toon-compliant structures.

## Capabilities

### Modified Capabilities
- `audio-transcription`: Update the output format requirement from JSON to the Toon protocol.
- `task-management`: Ensure all tools operate synchronously for maximum compatibility.

## Impact

- `src/features/audio_transcription/logic.py`: Update the return type and data mapping to TOON.
- `pyproject.toml`: Add `toon-format` dependency.
- Existing clients consuming JSON output from the transcription tool will need to be updated to handle the Toon protocol.
