# Task Management Specification

## Purpose
This specification defines the requirements for handling long-running operations in the system.

## Requirements

### Requirement: Synchronous Tool Execution
The system SHALL execute transcription tools synchronously by default to maintain simplicity and compatibility with standard MCP clients.

#### Scenario: Tool execution
- **WHEN** a client initiates the `transcribe_audio` tool
- **THEN** the system SHALL process the request and return the Toon-compliant result in a single response.
