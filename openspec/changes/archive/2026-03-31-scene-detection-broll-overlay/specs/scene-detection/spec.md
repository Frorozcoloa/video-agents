# Scene Detection Specification

## ADDED Requirements

### Requirement: Detect visual scene boundaries in a video file
The system SHALL analyze a video file using PySceneDetect's `ContentDetector` and return a list of detected scenes, each with a start and end timestamp in milliseconds.

#### Scenario: Successful scene detection
- **WHEN** a valid video file path is provided to the `video://{video_path}/scenes` MCP Resource
- **THEN** the system SHALL return a structured list of scenes, each containing `scene_number` (1-based integer), `start_ms` (integer), and `end_ms` (integer)

#### Scenario: Single-scene video
- **WHEN** a video file with no detectable cuts is provided
- **THEN** the system SHALL return a list with one scene covering the full duration (start_ms=0, end_ms=total_duration_ms)

### Requirement: Expose scene data as an MCP Resource
The system SHALL expose scene detection results as a FastMCP Resource using the URI template `video://{video_path}/scenes`, making scene data available as passive context for the LLM without requiring explicit tool invocation.

#### Scenario: Resource consumption by LLM
- **WHEN** the LLM reads the resource `video://{video_path}/scenes`
- **THEN** the system SHALL return the scene list as structured data (JSON-serializable)
- **AND** the resource SHALL NOT require any side-effect or action to produce the result

### Requirement: Timestamps in milliseconds
The system SHALL return all scene timestamps as integers in milliseconds for consistency with the rest of the video-agents pipeline.

#### Scenario: Millisecond precision
- **WHEN** PySceneDetect returns a `FrameTimecode` object
- **THEN** the system SHALL convert it to milliseconds using `timecode.get_seconds() * 1000` and cast to int

### Requirement: Error handling for invalid inputs
The system SHALL handle cases where the input file is missing or is not a valid video file.

#### Scenario: Missing video file
- **WHEN** the resource is requested with a path to a file that does not exist
- **THEN** the system SHALL raise an appropriate error indicating the file was not found

#### Scenario: Unreadable video file
- **WHEN** the resource is requested with a path to a file that cannot be decoded by OpenCV
- **THEN** the system SHALL raise an error indicating the file is not a valid video

### Requirement: Unit testing for scene detection logic
The core scene detection logic SHALL be verifiable through automated unit tests that mock the PySceneDetect output.

#### Scenario: Verify scene list construction
- **WHEN** the unit tests run with a mocked `detect_scenes` result
- **THEN** the tests SHALL confirm that `start_ms` and `end_ms` values are correctly computed from `FrameTimecode` objects and returned as integers
