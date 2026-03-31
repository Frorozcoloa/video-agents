## Context

The current `transcribe_audio` tool in the `video-agents` MCP server returns a standard JSON structure. This approach has two main drawbacks:
1. **Token Consumption**: JSON can be verbose, leading to high token usage in LLM responses.
2. **Standardization**: A more compact and formalized representation of temporal media data is needed for better efficiency.

To address these, we integrated the Toon protocol (using the `toon-format` library) to provide a more efficient data representation for transcription results.

## Goals / Non-Goals

**Goals:**
- Transition the `audio-transcription` output to the Toon protocol using `toon-format`.
- Maintain synchronous tool execution for simplicity and maximum compatibility with MCP clients.
- Add `toon-format` as a project dependency.

**Non-Goals:**
- Implementing asynchronous background tasks or polling mechanisms at this stage.
- Changing the underlying transcription engine (faster-whisper).

## Decisions

### 1. Data Protocol: Toon Protocol (via toon-format)
- **Decision**: Replace the current JSON output with a Toon-compliant structure.
- **Rationale**: TOON (Token-Oriented Object Notation) optimizes LLM interactions by reducing token consumption and structural noise.
- **Model Awareness**: The `transcribe_audio` tool description explicitly identifies the output format as **TOON**.

### 2. Execution Pattern: Synchronous
- **Decision**: Keep the tool execution synchronous.
- **Rationale**: While transcription can be slow, keeping it synchronous avoids the complexity of task management and polling, ensuring compatibility with all standard MCP clients. We mitigate timeout risks by optimizing model loading and inference.

## Risks / Trade-offs

- **[Risk] Timeouts** → Long audio files may still hit MCP timeout limits. **[Mitigation]** Use efficient Whisper models (e.g., `base`) and cache model instances.
- **[Risk] Breaking Change** → Existing clients expecting JSON will break. **[Mitigation]** Standardize on TOON for all temporal media data in the project.
