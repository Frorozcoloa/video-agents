## ADDED Requirements

### Requirement: Jump Cut Video Processing (Vertical Slice Architecture)
The system SHALL provide a decoupled, vertically integrated tool to generate "Jump Cut" videos by removing silences based on an independently provided audio file.

#### Scenario: Silence detection and millisecond timestamp orchestration
- **WHEN** a video and its corresponding audio file are processed through the tool layer
- **THEN** they SHALL become a strongly-typed `JumpCutRequest` object containing `video_path` and `audio_path`.
- **AND THEN** the domain logic layer SHALL manage Voice Activity Detection on the provided audio file, strictly returning all timestamps in **milliseconds** for interoperability.
- **AND THEN** the same domain layer SHALL delegate FFmpeg filter strings processing (`select`, `aselect`, `setpts=N/FRAME_RATE/TB`, `asetpts=N/SR/TB`) using those mapped times.
- **AND THEN** a standardized `JumpCutResponse` MUST be passed back, ensuring boundaries and synchronized jump-cuts.
