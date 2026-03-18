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

## 5. Infrastructure and Deployment (HTTP Sync)

- [x] 5.1 Set server transport to `http` (SSE) in `src/server.py`.
- [x] 5.2 Configure Docker port mapping for port 8000.
- [x] 5.3 Update `README.md` with Postman and Curl instructions for the new transport.
