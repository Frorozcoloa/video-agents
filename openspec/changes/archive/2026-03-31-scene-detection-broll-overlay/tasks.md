## 1. Scene Detection — Module Setup

- [x] 1.1 Create `src/features/scene_detection/` directory with `__init__.py`, `models.py`, `logic.py`, `tool.py`
- [x] 1.2 Define Pydantic models in `models.py`: `Scene(scene_number: int, start_ms: int, end_ms: int)` and `SceneList(scenes: list[Scene])`
- [x] 1.3 Implement `detect_scenes(video_path: str) -> list[Scene]` in `logic.py` using PySceneDetect `ContentDetector` (threshold=27.0), converting `FrameTimecode` to ms via `timecode.get_seconds() * 1000`
- [x] 1.4 Handle single-scene video: if no cuts detected, return one scene covering full duration (start_ms=0, end_ms=total_duration_ms)
- [x] 1.5 Add error handling: raise on missing file or unreadable video

## 2. Scene Detection — MCP Resource Registration

- [x] 2.1 In `tool.py`, register MCP Resource at `video://{video_path}/scenes` using `@mcp.resource()`, delegating to `detect_scenes` logic
- [x] 2.2 Format resource output as toon-format response
- [x] 2.3 Register scene detection in `src/server.py` via `register_scene_detection(mcp)`

## 3. Scene Detection — Tests

- [x] 3.1 Create `tests/test_scene_detection.py` with unit tests mocking PySceneDetect output
- [x] 3.2 Test correct ms conversion from `FrameTimecode` objects
- [x] 3.3 Test single-scene fallback (no cuts detected)
- [x] 3.4 Test error cases: missing file, invalid video
- [x] 3.5 Test MCP resource registration

## 4. B-roll Overlay — Module Setup

- [x] 4.1 Create `src/features/broll_overlay/` directory with `__init__.py`, `models.py`, `logic.py`, `tool.py`
- [x] 4.2 Define Pydantic models in `models.py`: `BrollRequest(video_path: str, broll_path: str, start_ms: int, end_ms: int, output_path: str | None)` with validator `start_ms < end_ms`
- [x] 4.3 Implement `apply_broll(request: BrollRequest) -> str` in `logic.py`: build FFmpeg complex filter graph with `overlay`, `eof_action=repeat`, scale B-roll to main video dimensions, pass through main audio
- [x] 4.4 Generate default output path with `_broll` suffix when `output_path` is None

## 5. B-roll Overlay — MCP Tool Registration

- [x] 5.1 In `tool.py`, register `apply_broll` MCP tool using `@mcp.tool()`, delegating to logic
- [x] 5.2 Format tool output as toon-format response
- [x] 5.3 Register B-roll overlay in `src/server.py` via `register_broll_overlay(mcp)`

## 6. B-roll Overlay — Tests

- [x] 6.1 Create `tests/test_broll_overlay.py` with unit tests mocking `ffmpeg.run`
- [x] 6.2 Test FFmpeg filter graph construction: verify `overlay`, `eof_action=repeat`, `scale` filter presence
- [x] 6.3 Test timestamp validation: start_ms >= end_ms raises error
- [x] 6.4 Test default output path generation
- [x] 6.5 Test audio preservation (main audio passed through, B-roll audio discarded)
- [x] 6.6 Test MCP tool registration
