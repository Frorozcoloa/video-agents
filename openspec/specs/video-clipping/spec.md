# Video Clipping Capability

## Purpose
The Video Clipping capability allows for extracting specific segments from video files based on provided start and end timestamps. It supports both fast (streamcopy) and exact (re-encoding) modes to balance speed and frame-level accuracy, with specific optimization for short-form content like YouTube Shorts.

## Requirements

### Requirement: Clip video segments by timestamps
The system SHALL provide a tool to extract a segment from a video file based on a start timestamp and an end timestamp, provided in milliseconds as an integer.

#### Scenario: Successful segment extraction in milliseconds
- **WHEN** a valid path to a video file is provided with start and end timestamps in milliseconds (e.g., 10500 for 10.5s)
- **THEN** the system SHALL return the path to the clipped video file containing only the specified segment.

### Requirement: Dynamic Duration for Social Media (YouTube Shorts)
The system SHALL support dynamic duration clipping by calculating the exact time difference between the provided start and end timestamps.

#### Scenario: Variable length clip for YouTube Shorts
- **WHEN** a user provides start and end timestamps for a segment (e.g., 15s, 30s, or 60s)
- **THEN** the system SHALL produce a video file with the exact duration requested, facilitating direct upload to social media platforms.

### Requirement: Support fast clipping mode (Streamcopy)
The system SHALL provide a "fast" mode that uses stream copying for speed, acknowledging it is limited to keyframes.

#### Scenario: Fast clipping execution
- **WHEN** the "fast" mode is selected for video clipping
- **THEN** the system SHALL use FFmpeg with the `-c copy` argument to extract the segment without re-encoding.

### Requirement: Support exact clipping mode (Frame-accurate)
The system SHALL provide an "exact" mode that ensures frame-accurate clipping by re-encoding the segment with high-quality settings.

#### Scenario: Exact clipping execution
- **WHEN** the "exact" mode is selected for video clipping
- **THEN** the system SHALL use FFmpeg with:
    - `libx264` video codec and `aac` audio codec.
    - `-ss` parameter before the input for fast seeking.
    - `-t` parameter for exact duration.
    - `crf=18` for high visual quality.
    - `preset="veryfast"` for processing speed balance.
    - `avoid_negative_ts="make_non_negative"` to ensure timestamp consistency in the output.

### Requirement: Validation of timestamps
The system SHALL validate that the start timestamp is less than the end timestamp and within the video's total duration.

#### Scenario: Invalid timestamp range
- **WHEN** the start timestamp is greater than or equal to the end timestamp
- **THEN** the system SHALL raise an error indicating the range is invalid.
