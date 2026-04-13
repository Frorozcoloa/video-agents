## 1. Feature Module Scaffold

- [x] 1.1 Create `src/features/audio_ducking/` directory with empty `__init__.py`
- [x] 1.2 Create `src/features/audio_ducking/models.py` with `AudioDuckingInput` (voice_path, music_path, output_path, threshold, ratio, attack, release) and `AudioDuckingOutput` (output_path, params) Pydantic models including field validators for threshold [0.0–1.0] and ratio ≥1.0
- [x] 1.3 Create `src/features/audio_ducking/logic.py` with `duck_audio(input: AudioDuckingInput) -> AudioDuckingOutput` that builds and runs the FFmpeg filter graph (asplit → sidechaincompress → amix with aformat stereo normalisation)
- [x] 1.4 Create `src/features/audio_ducking/tool.py` with `register_audio_ducking(mcp)` that registers the tool and wraps the response in toon-format

## 2. Server Registration

- [x] 2.1 Import `register_audio_ducking` in `src/server.py` and call it at startup alongside the other feature registrations

## 3. Unit Tests

- [x] 3.1 Create `tests/test_audio_ducking.py` with a test for successful registration (`test_audio_ducking_tool_registered`)
- [x] 3.2 Add test for `logic.py`: mock `ffmpeg` and assert the filter graph string contains `sidechaincompress`, correct threshold/ratio/release/attack values, and `aformat=channel_layouts=stereo`
- [x] 3.3 Add test for default parameters: assert defaults (threshold=0.1, ratio=5, attack=20, release=500) are passed when none are provided
- [x] 3.4 Add test for custom parameters: assert caller-supplied values override defaults in the filter graph
- [x] 3.5 Add validation tests: assert `AudioDuckingInput` raises `ValidationError` for threshold outside [0.0, 1.0] and ratio < 1.0
- [x] 3.6 Add test for missing voice file: assert tool returns error without invoking FFmpeg
- [x] 3.7 Add test for missing music file: assert tool returns error without invoking FFmpeg
- [x] 3.8 Add test for non-existent output directory: assert tool returns error without invoking FFmpeg

## 4. Verification

- [x] 4.1 Run `uv run pytest tests/test_audio_ducking.py -v` — all tests pass
- [x] 4.2 Run `uv run pytest --cov=src/features/audio_ducking` — coverage ≥80%
- [x] 4.3 Run `uv run pre-commit run --all-files` — no linting or formatting errors
