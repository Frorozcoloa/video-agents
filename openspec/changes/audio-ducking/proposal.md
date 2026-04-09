## Why

Video productions mixing voiceover with background music require the music to automatically attenuate when the speaker is active — this is called audio ducking. Without it, editors must manually keyframe volume on every voice segment, which is time-consuming and error-prone. This tool automates that process using FFmpeg's `sidechaincompress` filter.

## What Changes

- Add a new `audio_ducking` MCP tool that accepts a voice track and a music track and produces a mixed output where the music volume is automatically reduced when voice is present.
- Uses FFmpeg's `sidechaincompress` filter with `asplit` to route the voice signal as a sidechain trigger for the music compression.
- Exposes configurable parameters (threshold, ratio, release) with sensible defaults (threshold=0.1, ratio=5, release=500ms).

## Capabilities

### New Capabilities
- `audio-ducking`: Sidechain-compress a background music track against a voice track so the music attenuates automatically when voice is present, then mix both tracks into a single stereo output file.

### Modified Capabilities

## Impact

- **New files**: `src/features/audio_ducking/` (tool.py, models.py, logic.py), `tests/test_audio_ducking.py`
- **Modified files**: `src/server.py` (register new tool at startup)
- **Dependencies**: `ffmpeg-python` (already in project); no new dependencies required
- **API**: Exposes one new MCP tool `audio_ducking` with inputs `voice_path`, `music_path`, `output_path`, and optional compression parameters
