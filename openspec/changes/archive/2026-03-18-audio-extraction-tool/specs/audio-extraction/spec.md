## ADDED Requirements

### Requirement: Extract high-quality audio from video files
The system SHALL provide a mechanism to extract the audio track from a video file (e.g., .mp4) and save it as a high-quality .mp3 file.

#### Scenario: Successful audio extraction
- **WHEN** a valid path to an .mp4 video file is provided to the `extract_audio` tool
- **THEN** the system SHALL return the path to a newly created .mp3 file containing only the audio from the source video.

#### Scenario: High-quality encoding
- **WHEN** extracting audio
- **THEN** the system SHALL use the `libmp3lame` codec with a variable bitrate (VBR) setting of `q=2`.

#### Scenario: Video stream exclusion
- **WHEN** extracting audio
- **THEN** the system SHALL explicitly exclude the video stream from the output file (using `vn=None`).

### Requirement: Error handling for invalid inputs
The system SHALL handle cases where the input file is missing or is not a valid video file.

#### Scenario: Missing input file
- **WHEN** the `extract_audio` tool is called with a path to a file that does not exist
- **THEN** the system SHALL raise an appropriate error message indicating the file was not found.

#### Scenario: Invalid video file
- **WHEN** the `extract_audio` tool is called with a path to a file that is not a recognized video format
- **THEN** the system SHALL raise an error indicating the file format is invalid.

### Requirement: Unit Testing for Extraction Logic
The core audio extraction logic SHALL be verifiable through automated unit tests that mock the FFmpeg execution.

#### Scenario: Verify FFmpeg command generation
- **WHEN** running the unit tests for the extraction logic
- **THEN** the tests SHALL confirm that the FFmpeg command is correctly constructed with `vn=None`, `acodec='libmp3lame'`, and `q=2`.
