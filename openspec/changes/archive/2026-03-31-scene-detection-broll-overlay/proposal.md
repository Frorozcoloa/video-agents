## Why

The current pipeline can extract and transcribe audio but has no visibility into the video's visual structure. This feature closes that gap: it lets the LLM identify scene boundaries and decide which segments to replace with B-roll content, enabling narrative-driven automated editing.

## What Changes

- Integrate `PySceneDetect` to detect visual transitions in a video and expose the scene anchor points as an **MCP Resource** (not a tool), so the LLM can consume them as context without actively invoking a tool.
- Implement the `apply_broll` tool that accepts a main video, a B-roll clip, and a time range (start/end in ms), and overlays the B-roll onto the target segment using FFmpeg's `overlay` filter with `eof_action=repeat` to handle B-rolls shorter than the target segment.

## Capabilities

### New Capabilities
- `scene-detection`: Detects and exposes video scene cut points as a structured MCP Resource (list of scenes with start/end in ms).
- `broll-overlay`: Overlays a B-roll clip onto a specific segment of the main video using FFmpeg overlay with `eof_action=repeat` for B-rolls shorter than the target segment.

### Modified Capabilities
<!-- No existing specs change requirements -->

## Impact

- **New MCP Resource**: `video://{video_path}/scenes` exposes scene detection results.
- **New MCP Tool**: `apply_broll(video_path, broll_path, start_ms, end_ms, output_path?)`.
- **New features**: `src/features/scene_detection/` and `src/features/broll_overlay/` following the existing modular pattern (tool.py, models.py, logic.py).
- **Dependencies**: `scenedetect[opencv-headless]` is already in the project; `ffmpeg-python` already available.
- **Server**: `src/server.py` updated to register the new resource and tool.
