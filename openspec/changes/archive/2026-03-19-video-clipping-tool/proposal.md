## Why

Users need the ability to extract specific segments from video files based on start and end timestamps. Currently, the system supports audio extraction and transcription, but lacks the core video editing capability of clipping. Adding this tool enables precise video segment generation for downstream tasks like social media sharing or highlight reel creation.

## What Changes

- Add a new `video_clipping` feature to the MCP server.
- Implement a tool that accepts a video file path, and start/end timestamps in **milliseconds (integer)**.
- Support two clipping modes: fast (streamcopy) and exact (re-encoding).
- Register the new tool in the main MCP server.

## Capabilities

### New Capabilities
- `video-clipping`: Ability to cut a specific segment from a video file using start and end timestamps in **milliseconds (integer)**, supporting both fast (keyframe-based) and exact (frame-accurate) modes.

### Modified Capabilities
- None.

## Impact

- **New Feature**: `src/features/video_clipping/` will contain the logic, models, and tool registration.
- **Server Update**: `src/server.py` will be modified to register the new video clipping tool.
- **Dependencies**: Ensures `ffmpeg` is available in the environment (already part of the tech stack).
- **APIs**: New MCP tool `clip_video` exposed to clients.
