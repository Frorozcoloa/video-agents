## 1. Feature Setup

- [x] 1.1 Create `src/features/video_clipping/` directory with `__init__.py`.
- [x] 1.2 Define `ClippingRequest` and `ClippingResponse` models in `src/features/video_clipping/models.py`.

## 2. Core Implementation

- [x] 2.1 Implement `clip_video_logic` in `src/features/video_clipping/logic.py` using `ffmpeg-python`.
- [x] 2.2 Add support for "Fast Mode" using `vcodec='copy'` in the FFmpeg command.
- [x] 2.3 Add support for "Exact Mode" using `vcodec='libx264'` and `acodec='aac'` in the FFmpeg command.
- [x] 2.4 Implement timestamp validation (start < end) and file existence checks.

## 3. MCP Tool Registration

- [x] 3.1 Create `src/features/video_clipping/tool.py` and implement `register_video_clipping`.
- [x] 3.2 Update `src/server.py` to import and call `register_video_clipping`.

## 4. Testing and Validation

- [x] 4.1 Create `tests/test_video_clipping.py` with unit tests for `clip_video_logic` mocking FFmpeg.
- [x] 4.2 Verify Fast Mode command generation in unit tests.
- [x] 4.3 Verify Exact Mode command generation in unit tests.
- [x] 4.4 Run automated tests to ensure no regressions.
