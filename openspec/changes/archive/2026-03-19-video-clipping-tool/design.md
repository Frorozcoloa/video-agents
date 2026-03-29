## Context

The current system supports audio extraction and transcription but lacks a direct video manipulation tool. This design introduces a `video_clipping` feature that leverages FFmpeg to extract segments from video files.

## Goals / Non-Goals

**Goals:**
- Provide a frame-accurate video clipping tool.
- Provide a fast keyframe-based clipping tool for efficiency.
- Seamlessly integrate with the existing FastMCP server architecture.
- Ensure robust error handling for invalid timestamps or missing files.

**Non-Goals:**
- Complex video editing (transitions, overlays, etc.).
- Multi-clip stitching (concatenation).
- Format conversion (though re-encoding in exact mode is necessary).

## Decisions

- **FFmpeg Library**: Use `ffmpeg-python` for consistency with `audio_extraction`.
- **Clipping Modes**:
  - **Fast Mode**: Uses `-c copy` (streamcopy). This avoids re-encoding and is extremely fast but is limited to seeking to the nearest keyframe.
  - **Exact Mode**: Uses `-c:v libx264` and `-c:a aac`. By re-encoding, we ensure the clip starts and ends exactly at the requested timestamps.
- **Timestamp Accuracy**: Timestamps are provided in **milliseconds as integers** (e.g., 10500 for 10.5 seconds). For "Exact Mode", the `-ss` parameter will be placed *before* the input (`ffmpeg.input(..., ss=start)`) to enable fast seeking, and the output will be re-encoded to ensure frame precision.

## Risks / Trade-offs

- **[Risk]**: Fast mode might produce clips that start slightly before or after the requested timestamp due to keyframe alignment.
  - **[Mitigation]**: Explicitly document this limitation and provide the "Exact Mode" as an alternative.
- **[Risk]**: Re-encoding in Exact Mode can be CPU-intensive and slow for large segments.
  - **[Mitigation]**: Default to Fast Mode if not specified, or allow the user to choose.
- **[Risk]**: Input file might not have a seekable index.
  - **[Mitigation]**: FFmpeg usually handles this, but we will catch `ffmpeg.Error` and provide clear feedback.
