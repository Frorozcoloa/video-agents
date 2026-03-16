## Why

This change implements the first technical tool of the Proof of Concept (POC) to efficiently and cleanly separate an audio track from a video source. High-quality audio extraction is critical to ensure the accuracy of downstream transcription and analysis models, such as Whisper.

## What Changes

- Create a new MCP tool `extract_audio` that accepts a video file path and returns the path to the extracted audio.
- Integrate the `ffmpeg-python` library as the processing engine.
- Configure FFmpeg to discard video streams using the `vn=None` parameter.
- Implement high-quality MP3 encoding using the `libmp3lame` codec with a variable bitrate (VBR) setting of `q=2`.

## Capabilities

### New Capabilities
- `audio-extraction`: Provides the ability to extract high-quality audio from video files, optimized for AI transcription workflows.

### Modified Capabilities
-

## Impact

- **New MCP Tool**: Clients will have access to a new `extract_audio` tool.
- **Dependencies**: Adds `ffmpeg-python` to the project dependencies and requires `ffmpeg` to be installed on the system.
- **Server Registration**: Requires updates to `src/server.py` (or a dedicated feature module) to register the tool with the FastMCP server.
