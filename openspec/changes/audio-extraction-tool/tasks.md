## 1. Environment and Dependencies

- [x] 1.1 Add `ffmpeg-python` to `pyproject.toml` (or using `uv add`).
- [x] 1.2 Verify `ffmpeg` is installed and available in the system PATH.

## 2. Feature Structure and Models

- [x] 2.1 Create the directory `src/features/audio_extraction/`.
- [x] 2.2 Implement Pydantic models in `src/features/audio_extraction/models.py` (e.g., `ExtractionRequest`, `ExtractionResponse`).

## 3. Core Logic and Tool Implementation

- [x] 3.1 Implement the extraction logic in `src/features/audio_extraction/logic.py` using `ffmpeg-python`.
- [x] 3.2 Implement the tool registration in `src/features/audio_extraction/tool.py`.
- [x] 3.3 Register the `audio_extraction` feature in `src/server.py`.

## 4. Testing and Validation

- [x] 4.1 Create `tests/test_audio_extraction.py`.
- [x] 4.2 Write unit tests for `generate_extraction_logic` (or similar) mocking the FFmpeg command generation.
- [x] 4.3 Verify that the tool is correctly registered with the FastMCP server.
- [x] 4.4 Perform a manual validation with a small sample video (if possible).
