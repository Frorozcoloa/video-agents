# B-roll Overlay Specification

## ADDED Requirements

### Requirement: Overlay a B-roll clip onto a time-bounded segment of the main video
The system SHALL provide an `apply_broll` tool that composites a B-roll video clip over a specified time range of the main video, using FFmpeg's `overlay` filter.

#### Scenario: Successful B-roll overlay
- **WHEN** a valid main video path, a valid B-roll path, and a time range (start_ms, end_ms) are provided
- **THEN** the system SHALL return the path to a new video file where the B-roll is composited over the main video for the specified segment

#### Scenario: Optional output path
- **WHEN** no output path is provided
- **THEN** the system SHALL generate an output path in the same directory as the main video with a `_broll` suffix

### Requirement: Handle B-roll shorter than the target segment using eof_action=repeat
The system SHALL use `eof_action=repeat` in the FFmpeg overlay filter to freeze the last frame of the B-roll when it is shorter than the target segment, preventing black frames or abrupt endings.

#### Scenario: B-roll shorter than segment
- **WHEN** the B-roll duration is less than `(end_ms - start_ms)` milliseconds
- **THEN** the system SHALL apply `eof_action=repeat` so the last frame of the B-roll is held for the remainder of the segment

#### Scenario: B-roll equal to or longer than segment
- **WHEN** the B-roll duration is greater than or equal to `(end_ms - start_ms)` milliseconds
- **THEN** the system SHALL trim the B-roll to the segment duration

### Requirement: Scale B-roll to match main video dimensions
The system SHALL scale the B-roll clip to match the width and height of the main video before compositing.

#### Scenario: Resolution mismatch
- **WHEN** the B-roll has different dimensions than the main video
- **THEN** the system SHALL apply an FFmpeg `scale` filter to resize the B-roll to the main video's width and height before overlaying

### Requirement: Preserve main video audio track
The system SHALL pass through the main video's audio track unchanged; B-roll audio SHALL be discarded.

#### Scenario: Audio preservation
- **WHEN** the B-roll overlay is applied
- **THEN** the output video SHALL contain only the original main video audio stream

### Requirement: Validate timestamp range
The system SHALL validate that the provided start_ms is less than end_ms.

#### Scenario: Invalid timestamp range
- **WHEN** start_ms is greater than or equal to end_ms
- **THEN** the system SHALL raise a validation error before invoking FFmpeg

### Requirement: Unit testing for overlay logic
The core B-roll overlay logic SHALL be verifiable through automated unit tests that mock FFmpeg execution.

#### Scenario: Verify FFmpeg filter graph construction
- **WHEN** the unit tests run with mocked `ffmpeg.run`
- **THEN** the tests SHALL confirm the overlay filter is constructed with `eof_action=repeat` and the correct start/end timestamps
