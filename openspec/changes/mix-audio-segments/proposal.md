## Why

`replace_audio` swaps the entire audio track of a video. Editors often need finer control: place a sound effect at second 5, a voiceover from second 12 to 20, and background music from second 30 onward — all layered over the original video audio. A `mix_audio_segments` tool closes this gap by accepting a list of timed audio segments and mixing each one into the video at the specified position.

## What Changes

- Add a new `mix_audio_segments` MCP tool that accepts a video path and a list of segments, each with an audio file path, a start time (ms), and an end time (ms).
- Each segment audio is trimmed to its duration, delayed to its start position, and mixed over the original video audio using FFmpeg's `adelay`, `atrim`, and `amix` filters.
- The original video audio is always preserved; segments are layered on top (additive mix).
- Output defaults to the input video path with a `_mixed` suffix if not specified.

## Capabilities

### New Capabilities
- `mix-audio-segments`: Place one or more audio clips at specific time positions over a video's original audio track. Each segment is defined by `{audio_path, start_ms, end_ms}`. Uses FFmpeg `adelay` + `atrim` + `amix` to compose all streams in a single pass.

### Modified Capabilities

## Impact

- **New files**: `src/features/mix_audio_segments/` (tool.py, models.py, logic.py), `tests/test_mix_audio_segments.py`
- **Modified files**: `src/server.py` (register new tool)
- **Dependencies**: `ffmpeg-python` (already in project); no new dependencies
- **API**: Exposes one new MCP tool `mix_audio_segments` with inputs `video_path`, `segments` (list), and optional `output_path`
