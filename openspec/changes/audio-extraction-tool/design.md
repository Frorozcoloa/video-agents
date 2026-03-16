## Context

The current project has a basic FastMCP server with a "Hello World" feature. This design introduces the first media processing feature: high-quality audio extraction from video files using FFmpeg.

## Goals / Non-Goals

**Goals:**
- Implement a robust `extract_audio` tool.
- Use `ffmpeg-python` for process management.
- Ensure high-quality MP3 output (VBR q=2, libmp3lame).
- Maintain a clean separation between the MCP tool interface and the extraction logic.
- Include unit tests that verify the logic and command generation.

**Non-Goals:**
- Supporting multiple output formats (only MP3 for now).
- Handling real-time streaming (file-to-file only).
- Advanced audio post-processing (e.g., noise reduction).

## Decisions

- **Feature Structure**: Follow the existing pattern in `src/features/`. Create `src/features/audio_extraction/` with `tool.py`, `logic.py`, and `models.py`.
- **FFmpeg Integration**: Use `ffmpeg-python` (wrapper for `ffmpeg`) to provide a Pythonic API for building FFmpeg commands.
- **Testing Strategy**:
    - Use `pytest` for unit testing.
    - Mock `ffmpeg.run` to verify that the correct parameters (`vn=None`, `acodec='libmp3lame'`, `q=2`) are passed without actually running FFmpeg during unit tests.
    - Create a separate integration test (optional/manual) for actual file processing if a sample video is available.

## Risks / Trade-offs

- **[Risk] FFmpeg Dependency** → FFmpeg must be installed on the host system. **Mitigation**: Add a check for FFmpeg availability on server startup or tool invocation.
- **[Risk] Performance** → Media processing is CPU-intensive. **Mitigation**: Although this POC uses standard synchronous calls, the design will allow for future migration to the asynchronous processing planned in Issue 8.
- **[Trade-off] MP3 vs WAV** → MP3 (Lossy) vs WAV (Lossless). **Decision**: MP3 with high VBR (q=2) is chosen to balance quality and file size, which is sufficient for Whisper transcription.
