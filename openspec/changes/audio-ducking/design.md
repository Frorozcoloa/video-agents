## Context

The video-agents MCP server already provides audio extraction, transcription, and video clipping tools. Audio ducking is the next natural step for post-production automation: automatically lower background music whenever a voice track is active. FFmpeg's `sidechaincompress` filter performs this natively, requiring no ML inference and no new dependencies beyond the already-used `ffmpeg-python`.

## Goals / Non-Goals

**Goals:**
- Expose an `audio_ducking` MCP tool that accepts a voice path, music path, and output path
- Apply sidechain compression using FFmpeg (`sidechaincompress` + `asplit` + `amix`) to produce a single mixed stereo output
- Support configurable compression parameters with safe defaults (threshold=0.1, ratio=5, release=500ms)
- Follow the feature module pattern (`tool.py`, `models.py`, `logic.py`) consistent with all other features
- Achieve ≥80% test coverage with mocked FFmpeg calls

**Non-Goals:**
- Real-time or streaming audio ducking
- Voice activity detection (VAD) — the sidechain compressor is signal-driven, not VAD-driven
- Multi-track ducking (more than one voice or more than one music track)
- GPU acceleration

## Decisions

### D1: Use FFmpeg `sidechaincompress` over manual VAD + volume keyframing
**Decision**: Use FFmpeg's native `sidechaincompress` filter.
**Rationale**: It processes audio in a single FFmpeg pass, is battle-tested, and produces smooth gain reduction with configurable attack/release envelopes. Manual VAD-driven volume ramping would require a two-pass pipeline (detect → apply), adding latency and complexity.
**Alternative considered**: Silero VAD + `volume` filter with keyframes — rejected because it requires a Python-side temporal loop and multiple FFmpeg invocations.

### D2: FFmpeg filter graph topology
**Decision**: `asplit` the voice track into (sidechain trigger, passthrough voice), compress the music against the voice sidechain, then `amix` voice + ducked music.

Filter graph:
```
voice_input  → asplit → [sc_trigger] ─────────────────────────────┐
                       → [voice_pass]                              ↓
music_input  ──────────────────────────── sidechaincompress ──→ [ducked_music]
                                                                   ↓
[voice_pass] + [ducked_music] → amix=inputs=2 → output
```

**Rationale**: This is the canonical FFmpeg ducking pattern. Using `asplit` avoids re-decoding the voice stream. `amix` normalises both channels to the same sample rate/format before merge.

### D3: Default compression parameters
| Parameter | Default | Rationale |
|-----------|---------|-----------|
| threshold | 0.1 | Triggers compression at 10% of full-scale — catches conversational voice without false positives |
| ratio | 5 | 5:1 reduces music to ~20% gain above threshold — audible but not complete silence |
| release | 500 ms | Prevents pumping artifacts on short pauses in speech |
| attack | 20 ms | Fast enough to catch word onsets without clipping |

### D4: All parameters exposed but optional
**Decision**: `threshold`, `ratio`, `release`, and `attack` are optional Pydantic fields with defaults.
**Rationale**: Advanced users may need to tune for different voice/music dynamics; however, defaults should work for 90% of cases.

## Risks / Trade-offs

- **FFmpeg version compatibility** → `sidechaincompress` has been available since FFmpeg 3.x; the Docker base image pins a recent version, so this is low risk. Mitigation: document minimum FFmpeg version in error message if filter is unavailable.
- **Mono vs. stereo input handling** → FFmpeg will error if channel counts mismatch. Mitigation: use `aformat=channel_layouts=stereo` on both inputs before the filter graph.
- **Very long files** → FFmpeg processes in a single pass and streams output; memory usage is bounded. No mitigation needed.
- **Output format** → Logic layer writes whatever extension the caller provides (`.wav`, `.mp3`, `.aac`). Mitigation: validate output extension in Pydantic model; default to `.wav` for lossless fidelity.
