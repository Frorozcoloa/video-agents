# Mix Audio Segments

Layer one or more timed audio clips over the original audio track of a video. Each segment defines an audio file and a time range; the original audio is preserved at full volume and segments are mixed on top additively using FFmpeg's `adelay` + `atrim` + `amix` filters in a single pass.

## Requirements

### Requirement: Accept video and a list of timed audio segments
The tool SHALL accept a video file path and a non-empty list of segments. Each segment MUST contain `audio_path` (str), `start_ms` (int ≥ 0), and `end_ms` (int > start_ms). The tool SHALL validate all inputs before invoking FFmpeg.

#### Scenario: Valid video and segments provided
- **WHEN** `video_path` exists and all segments have valid paths and time ranges
- **THEN** the tool proceeds to mix without error

#### Scenario: Empty segment list
- **WHEN** `segments` is an empty list
- **THEN** the tool returns a validation error without invoking FFmpeg

#### Scenario: Segment audio file does not exist
- **WHEN** any segment's `audio_path` points to a non-existent file
- **THEN** the tool returns an error without invoking FFmpeg

#### Scenario: start_ms greater than or equal to end_ms
- **WHEN** any segment has `start_ms >= end_ms`
- **THEN** the tool returns a validation error without invoking FFmpeg

#### Scenario: Negative start_ms
- **WHEN** any segment has `start_ms < 0`
- **THEN** the tool returns a validation error without invoking FFmpeg

---

### Requirement: Layer segments additively over original video audio
The tool SHALL preserve the original video audio track and mix each segment on top using FFmpeg's `amix` filter with `normalize=0`. The original audio SHALL play at full volume regardless of how many segments are active.

#### Scenario: Single segment mixed over original audio
- **WHEN** one segment is provided
- **THEN** the output contains the original audio plus the segment audio at the specified time range

#### Scenario: Multiple segments mixed simultaneously
- **WHEN** two or more segments overlap in time
- **THEN** all are mixed additively (both play simultaneously) and the original audio is preserved

#### Scenario: normalize=0 applied to amix
- **WHEN** the FFmpeg filter graph is built
- **THEN** `amix` is called with `normalize=0` to prevent volume reduction

---

### Requirement: Trim and position each segment precisely
Each segment audio SHALL be trimmed to `(end_ms - start_ms)` milliseconds using `atrim` and then delayed by `start_ms` milliseconds using `adelay` before mixing.

#### Scenario: Segment trimmed to declared duration
- **WHEN** a segment has `start_ms=5000` and `end_ms=10000`
- **THEN** `atrim` is applied with `duration=5.0` seconds

#### Scenario: Segment delayed to start position
- **WHEN** a segment has `start_ms=5000`
- **THEN** `adelay` is applied with delay value `5000` milliseconds on all channels

---

### Requirement: Output path defaults to input with `_mixed` suffix
If `output_path` is not provided, the tool SHALL derive it from the video filename by appending `_mixed` before the extension.

#### Scenario: No output path provided
- **WHEN** `output_path` is omitted
- **THEN** the output file path is `{video_stem}_mixed{video_ext}`

#### Scenario: Explicit output path respected
- **WHEN** `output_path` is provided
- **THEN** the output file is written to exactly that path

---

### Requirement: Validate output directory and video file existence
The tool SHALL verify the video file exists and the output directory exists before invoking FFmpeg.

#### Scenario: Video file does not exist
- **WHEN** `video_path` points to a non-existent file
- **THEN** the tool returns an error without invoking FFmpeg

#### Scenario: Output directory does not exist
- **WHEN** the directory of `output_path` does not exist
- **THEN** the tool returns an error without invoking FFmpeg

---

### Requirement: Return structured toon-format response
The tool SHALL return a response wrapped in `toon-format` containing the output path and the number of segments mixed.

#### Scenario: Successful response structure
- **WHEN** mixing completes without error
- **THEN** the response contains `output_path` and `segments_count`
