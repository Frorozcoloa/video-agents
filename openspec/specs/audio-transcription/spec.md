# Audio Transcription Specification

## Purpose
This specification defines the requirements for extracting text from audio files with high precision and word-level timestamps.

## Requirements

### Requirement: VAD Pre-processing
The system SHALL pre-process audio files using Silero-VAD to detect and remove silences and background noise before initiating transcription.

#### Scenario: Silence detection and removal
- **WHEN** an audio file with more than 2 seconds of silence is provided
- **THEN** the VAD SHALL segment the audio to process only portions containing speech.

### Requirement: Transcription with Word-Level Timestamps
The system SHALL use the `faster-whisper` engine to convert audio to text, ensuring that the `word_timestamps=True` parameter is activated.

#### Scenario: Successful transcription with precision
- **WHEN** a valid MP3/WAV file is processed
- **THEN** the system SHALL return a transcription where every segment has an associated start and end time in milliseconds.

### Requirement: Standardized Toon Protocol Output
The system SHALL return the transcription results in a structure compliant with the Toon protocol (using `toon-format`) to reduce token consumption in model responses.

#### Scenario: Toon Protocol Output Format
- **WHEN** the transcription task is complete
- **THEN** the system SHALL return a Toon document that is more compact than JSON.

### Requirement: Model-Explicit Documentation
The system SHALL explicitly state in the `transcribe_audio` tool description that it returns a Toon-compliant document.

#### Scenario: Tool Description Awareness
- **WHEN** a model (LLM) reads the tool definition for `transcribe_audio`
- **THEN** it SHALL be clearly informed that the output is in the `Toon` protocol format.
