## Context

The `video-agents` MCP server currently processes audio (extraction, transcription) and video (clipping, jump cuts) but has no concept of visual scene structure. This design introduces two tightly related capabilities: scene detection (read) and B-roll overlay (write). The LLM first reads scene boundaries via a Resource, then invokes a tool to overlay a B-roll clip on a chosen segment.

Both capabilities are implemented as separate feature modules (`scene_detection`, `broll_overlay`) following the existing pattern in `src/features/`.

## Goals / Non-Goals

**Goals:**
- Expose PySceneDetect output as a FastMCP Resource so the LLM can read scene structure as context.
- Implement `apply_broll` tool: overlay a B-roll clip on a time-bounded segment of the main video using FFmpeg's `overlay` filter.
- Handle B-roll shorter than the target segment via `eof_action=repeat`.
- Keep both features independently testable (mocked FFmpeg and scenedetect in unit tests).

**Non-Goals:**
- Real-time or streaming scene detection.
- Multiple simultaneous B-roll overlays in a single call (one segment per call).
- Audio mixing from the B-roll (video-only overlay; main audio track preserved).
- Scene detection threshold tuning exposed to the LLM (use sensible defaults).

## Decisions

### 1. Scene Detection → MCP Resource (not Tool)

**Decision**: Expose scenes via a FastMCP Resource at URI `video://{video_path}/scenes`, not as a tool.

**Rationale**: Resources are passively consumed by the LLM as context — no explicit invocation needed. Scene data is read-only metadata; modeling it as a Resource aligns with MCP semantics and avoids unnecessary round-trips. The LLM can consult scene boundaries naturally while planning edits.

**Alternative considered**: Exposing as a `detect_scenes` tool. Rejected because tools imply action/side-effects; scene detection is a pure read operation.

**Implementation**: Use `@mcp.resource("video://{video_path}/scenes")` in `src/features/scene_detection/tool.py`. PySceneDetect's `ContentDetector` runs synchronously on the file and returns a list of `Scene` objects with `start_ms` and `end_ms`.

### 2. B-roll Overlay via FFmpeg `overlay` Filter

**Decision**: Use FFmpeg complex filter graph with `overlay` filter and `eof_action=repeat`.

**Rationale**: The `overlay` filter is the standard FFmpeg primitive for compositing two video streams. `eof_action=repeat` freezes the last B-roll frame when the B-roll is shorter than the segment, avoiding black frames or abrupt endings.

**Filter graph structure**:
```
[0:v] trim=start={s}/end={e}, setpts=PTS-STARTPTS [base_segment];
[1:v] scale={w}:{h} [broll_scaled];
[base_segment][broll_scaled] overlay=eof_action=repeat [overlaid];
[0:v][overlaid] overlay=enable='between(t,{s},{e})' [out]
```
The main video audio track is passed through unchanged.

**Alternative considered**: `movie` filter with `shortest=0`. More complex to parameterize; `overlay` is more idiomatic and better supported by `ffmpeg-python`.

### 3. Feature Module Separation

**Decision**: Two separate feature modules — `scene_detection` and `broll_overlay` — each with `tool.py`, `models.py`, `logic.py`.

**Rationale**: They have distinct responsibilities (read vs. write), different MCP primitives (Resource vs. Tool), and should be independently testable. Co-locating them would couple their test surfaces.

### 4. Timestamps in Milliseconds

**Decision**: All public interfaces (Resource output, tool inputs) use milliseconds as integers, consistent with the rest of the codebase.

**Implementation**: PySceneDetect returns `FrameTimecode` objects; convert to ms via `timecode.get_seconds() * 1000`.

### 5. PySceneDetect Detector

**Decision**: Use `ContentDetector` with default threshold (27.0).

**Rationale**: `ContentDetector` detects cuts based on frame content differences — appropriate for general-purpose scene detection. Threshold is a sensible default; not exposed to the LLM to keep the interface simple.

## Risks / Trade-offs

- **[Risk] Large video files slow scene detection** → `ContentDetector` processes frames sequentially; large files can take seconds. **Mitigation**: The Resource is fetched on-demand; no background caching for now. Document expected latency in tool description.
- **[Risk] B-roll resolution mismatch** → If B-roll dimensions differ from the main video, the overlay may misalign. **Mitigation**: Scale B-roll to match main video dimensions before overlaying (`scale={w}:{h}`).
- **[Risk] FFmpeg filter graph complexity** → Complex filter chains are harder to debug. **Mitigation**: Build the filter string step-by-step in `logic.py` with clear variable names; validate with unit tests mocking `ffmpeg.run`.
- **[Trade-off] Audio not mixed** → B-roll audio is discarded; main audio is preserved. Simpler implementation; audio mixing is out of scope for this iteration.
