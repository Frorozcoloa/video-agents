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

### Requirement: Standardized JSON Output
The system SHALL return the transcription results in a structured JSON array of segments.

#### Scenario: JSON Output Format
- **WHEN** the transcription is complete
- **THEN** the system SHALL return an array of objects, each containing:
  - `"texto"`: The transcribed string.
  - `"tiempo_inicio"`: Start time in milliseconds (integer).
  - `"tiempo_fin"`: End time in milliseconds (integer).
