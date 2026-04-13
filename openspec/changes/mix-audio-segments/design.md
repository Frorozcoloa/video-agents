## Context

The pipeline now has `extract_audio`, `audio_ducking`, and `replace_audio`. The missing capability is placing audio clips at specific timestamps over the original video audio. This is common for sound design, voiceover insertion, and music cue placement without destroying the original audio bed.

## Goals / Non-Goals

**Goals:**
- Accept N segments `{audio_path, start_ms, end_ms}` and a video path
- Preserve the original video audio; segments are layered additively
- Process in a single FFmpeg pass regardless of segment count
- Validate all segment files exist and time ranges are valid (start < end, no negatives) before FFmpeg is invoked
- Follow the feature module pattern

**Non-Goals:**
- Replacing (not mixing) audio in a range — use `replace_audio` for that
- Crossfade or envelope between segments
- Segments that overlap each other (behaviour is additive — both play simultaneously, which is FFmpeg's default `amix` behaviour)

## Decisions

### D1: FFmpeg filter graph — `adelay` + `atrim` + `amix`
**Decision**: For each segment, apply `atrim=duration=<segment_duration_s>` then `adelay=<start_ms>|<start_ms>` to position it. Extract the original video audio and `amix` all streams together.

Filter graph for N segments:
```
video_audio ────────────────────────────────────────────────┐
seg0_audio → atrim(dur=d0) → adelay(start0|start0) ─────────┤
seg1_audio → atrim(dur=d1) → adelay(start1|start1) ─────────┤
...                                                          ↓
                                              amix(inputs=N+1, normalize=0)
```

`normalize=0` on `amix` prevents volume reduction when multiple streams are active — the original audio stays at full volume.

**Alternative considered**: `apad` + `aresample` chains — more complex and less readable.

### D2: `normalize=0` on `amix`
**Decision**: Disable normalisation.
**Rationale**: With normalisation enabled (default), FFmpeg reduces all stream volumes proportionally when mixing — e.g. with 3 inputs each plays at 33% volume. We want the original audio at 100% and segments layered on top at their natural volume.

### D3: `atrim` before `adelay`
**Decision**: Trim the segment audio to its target duration before delaying.
**Rationale**: Without trimming, a long audio file will play past its `end_ms` boundary. Trimming first ensures the segment stops at `end_ms - start_ms`.

### D4: Segment validation order
1. All `audio_path` files exist
2. All `start_ms >= 0`
3. All `start_ms < end_ms`
4. At least one segment provided

Validated in Pydantic models before logic is called.

### D5: Output path default
`{video_stem}_mixed{video_ext}` — consistent with `_replaced` and `_broll` suffixes.

## Risks / Trade-offs

- **Volume clipping**: If many segments overlap, the summed amplitude may clip. Mitigation: document that callers should control segment volumes externally; `normalize=0` is the correct tradeoff for typical use.
- **Segment audio shorter than declared duration**: `atrim` will trim to whichever is shorter — the file or `end_ms - start_ms`. No padding is added; silence is not inserted. This is expected.
- **Container audio codec compatibility**: Same risk as `replace_audio` — FFmpeg will error on incompatible codec/container combos. Pass through with descriptive message.
