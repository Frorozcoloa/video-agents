## 1. Feature Module Scaffold

- [x] 1.1 Create `src/features/mix_audio_segments/` directory with empty `__init__.py`
- [x] 1.2 Create `src/features/mix_audio_segments/models.py` with `AudioSegment` (audio_path, start_ms, end_ms with validators), `MixAudioSegmentsInput` (video_path, segments, output_path optional), and `MixAudioSegmentsOutput` (output_path, segments_count)
- [x] 1.3 Create `src/features/mix_audio_segments/logic.py` with `mix_audio_segments_logic(input)` that builds the FFmpeg filter graph: original video audio + each segment through `atrim` → `adelay` → `amix(normalize=0)`
- [x] 1.4 Create `src/features/mix_audio_segments/tool.py` with `register_mix_audio_segments(mcp)` that registers the tool and returns toon-format response

## 2. Server Registration

- [x] 2.1 Import `register_mix_audio_segments` in `src/server.py` and call it at startup

## 3. Unit Tests

- [x] 3.1 Create `tests/test_mix_audio_segments.py` with registration test (`test_mix_audio_segments_tool_registered`)
- [x] 3.2 Add test: single segment — assert `atrim`, `adelay`, and `amix` with `normalize=0` appear in the filter graph
- [x] 3.3 Add test: multiple segments — assert `amix` receives `inputs=N+1` where N is the segment count
- [x] 3.4 Add test: segment trimmed to correct duration — assert `atrim(duration=(end_ms-start_ms)/1000)`
- [x] 3.5 Add test: segment delayed to correct start — assert `adelay` called with `start_ms` value
- [x] 3.6 Add test: default output path is `{stem}_mixed{ext}`
- [x] 3.7 Add validation tests: empty segments list, start_ms >= end_ms, negative start_ms
- [x] 3.8 Add test: missing video file raises without invoking FFmpeg
- [x] 3.9 Add test: missing segment audio file raises without invoking FFmpeg
- [x] 3.10 Add test: non-existent output directory raises without invoking FFmpeg

## 4. Verification

- [x] 4.1 Run `uv run pytest tests/test_mix_audio_segments.py -v` — all tests pass
- [x] 4.2 Run `uv run pytest --cov=src/features/mix_audio_segments` — coverage ≥80%
- [x] 4.3 Run `uv run pre-commit run --all-files` — no linting or formatting errors
