## 1. Project Setup & Dependencies

- [x] 1.1 Add `toon-format` to `pyproject.toml` dependencies
- [x] 1.2 Run `uv sync` to install new dependencies

## 2. Audio Transcription Refactoring

- [x] 2.1 Implement `toon-format` encoding in `src/features/audio_transcription/logic.py`
- [x] 2.2 Ensure the transcription logic remains synchronous for maximum compatibility
- [x] 2.3 Modify `src/features/audio_transcription/tool.py` to use `@mcp.tool()` (sync)
- [x] 2.4 Update tool description to explicitly mention the `TOON` protocol
- [x] 2.5 Ensure the tool accepts an optional `progress` parameter to prevent Pydantic validation errors

## 3. Validation & Testing

- [x] 3.1 Update `tests/test_audio_transcription.py` to match sync implementation
- [x] 3.2 Add test cases to verify the final Toon output structure
- [x] 3.3 Verify all tests pass with over 80% coverage
