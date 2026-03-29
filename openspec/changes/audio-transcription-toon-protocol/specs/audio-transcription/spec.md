## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Standardized JSON Output
**Reason**: Replaced by the Toon protocol for better standardization and interoperability.
**Migration**: Update clients to consume the Toon protocol format provided by the transcription tool.
