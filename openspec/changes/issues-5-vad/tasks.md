## 1. Domain Types (Vertical Slice)
- [x] 1.1 In `src/features/video_clipping/models.py`, create `JumpCutRequest(video_path, output_video_path)`.
- [x] 1.2 In the same file, create `JumpCutResponse(video_path, success, cut_count)`.

## 2. Handler & Orchestration (VSA)
- [x] 2.1 Refactor the jump-cut logic in `src/features/video_clipping/logic.py` (or a dedicated `jump_cut.py`) into smaller, testable sub-functions:
  - `_extract_audio_for_vad(video_path) -> str`
  - `_detect_speech(audio_path) -> list`
  - `_apply_ffmpeg_jump_cut(video_path, output_path, timestamps) -> str`
- [x] 2.2 Create the main handler `process_jump_cut(request: JumpCutRequest) -> JumpCutResponse` that calls these sequentially.

## 3. Tool Registration Endpoint
- [x] 3.1 Update `jump_cut_video` tool in `src/features/video_clipping/tool.py` to instantiate `JumpCutRequest` and call `process_jump_cut()`.
- [x] 3.2 Ensure the tool *only* handles the @mcp boundary and doesn't orchestrate any I/O directly.

## 4. Testing & Validation
- [x] 4.1 Create test cases in `tests/test_jump_cut.py` using a mock video that contains simulated speech and silences.
- [x] 4.2 Verify that output plays smoothly without audio/video desync.
- [x] 4.3 Ensure test coverage exceeds 80%.
