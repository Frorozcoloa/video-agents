# Audio Ducking

Automatically attenuate background music when voice is present using FFmpeg's `sidechaincompress` filter. Accepts a voice track and a music track, applies sidechain compression, and produces a single mixed stereo output file.

## Requirements

### Requirement: Accept voice and music inputs
The tool SHALL accept a voice audio file path and a music audio file path as required inputs. Both paths MUST refer to existing, readable files. The tool SHALL validate both paths before initiating processing and return a descriptive error if either is missing or unreadable.

#### Scenario: Both inputs provided and valid
- **WHEN** `voice_path` and `music_path` point to existing audio files
- **THEN** the tool proceeds to mix them without error

#### Scenario: Voice file does not exist
- **WHEN** `voice_path` points to a non-existent file
- **THEN** the tool returns an error indicating the voice file was not found

#### Scenario: Music file does not exist
- **WHEN** `music_path` points to a non-existent file
- **THEN** the tool returns an error indicating the music file was not found

---

### Requirement: Produce a single mixed output file
The tool SHALL produce one output audio file at the caller-specified `output_path`. The output SHALL contain both the original voice track and the sidechain-compressed music track mixed together in stereo.

#### Scenario: Successful mix
- **WHEN** both inputs are valid and FFmpeg completes successfully
- **THEN** an audio file exists at `output_path` containing the mixed result

#### Scenario: Output directory does not exist
- **WHEN** the directory of `output_path` does not exist
- **THEN** the tool returns an error before attempting FFmpeg processing

---

### Requirement: Apply sidechain compression with default parameters
The tool SHALL apply FFmpeg's `sidechaincompress` filter using the voice track as the sidechain trigger and the music track as the compressed signal. Default parameters SHALL be: threshold=0.1, ratio=5, attack=20ms, release=500ms.

#### Scenario: Default parameters produce audible ducking
- **WHEN** the tool is called without specifying compression parameters
- **THEN** FFmpeg receives threshold=0.1, ratio=5, attack=20, release=500 in the filter graph

#### Scenario: Custom parameters override defaults
- **WHEN** the caller provides `threshold=0.05`, `ratio=8`, `attack=10`, `release=300`
- **THEN** FFmpeg receives those exact values in the filter graph

---

### Requirement: Support configurable compression parameters
The tool SHALL expose `threshold` (float, 0.0–1.0), `ratio` (float, ≥1.0), `attack` (int, milliseconds, ≥1), and `release` (int, milliseconds, ≥1) as optional parameters. Invalid values MUST be rejected before FFmpeg is invoked.

#### Scenario: Threshold out of range
- **WHEN** `threshold` is set to a value outside [0.0, 1.0]
- **THEN** the tool returns a validation error without invoking FFmpeg

#### Scenario: Ratio below minimum
- **WHEN** `ratio` is set below 1.0
- **THEN** the tool returns a validation error without invoking FFmpeg

---

### Requirement: Normalise channel layout before mixing
The tool SHALL ensure both input streams are converted to stereo (`channel_layouts=stereo`) using `aformat` before the sidechain filter graph to prevent FFmpeg channel mismatch errors.

#### Scenario: Mono voice input
- **WHEN** the voice file contains a single mono channel
- **THEN** it is up-mixed to stereo before being used as the sidechain trigger, and the output is stereo

#### Scenario: Stereo inputs
- **WHEN** both inputs are already stereo
- **THEN** no channel conversion artefacts are introduced and the output is stereo

---

### Requirement: Return structured toon-format response
The tool SHALL return a response wrapped in the project's `toon-format` protocol, including the output file path and the compression parameters actually applied.

#### Scenario: Successful response structure
- **WHEN** the mix completes without error
- **THEN** the response contains `output_path` and a `params` object with the applied threshold, ratio, attack, and release values
