# Design: VAD for Jump Cuts (Vertical Slice Architecture)

## Architecture
This feature follows the **Vertical Slice Architecture** pattern, ensuring that the "Jump Cut" use case is entirely encapsulated within its own slice, distinct from standard clipping, while sharing the same feature boundaries (`src/features/video_clipping/`).

### Layer Separation
1. **MCP Tool Layer (`tool.py`)**:
   - Registers the `@mcp.tool()`.
   - Parses raw arguments into a strong Pydantic model (`JumpCutRequest`).
   - Delegates execution to the handler and unpacks the `JumpCutResponse`.
2. **Model Layer (`models.py`)**:
   - `JumpCutRequest`: Validates input (`video_path`, optional `output_path`).
   - `JumpCutResponse`: Standardizes output (`video_path`, `success`, `segments_processed`).
3. **Logic / Handler Layer (`logic.py` / `jump_cut.py`)**:
   - Contains `process_jump_cut(request: JumpCutRequest) -> JumpCutResponse`.
   - Orchestrates the sub-components without bleeding domain logic into the tool layer.

### Core Processing Flow
The logic layer orchestrates three distinct sub-processes to adhere to the Single Responsibility Principle:
1. **Audio Preparation**: `_prepare_audio_for_vad(audio_path)` -> Reads the independently extracted audio file and ensures a 16kHz WAV format required by the VAD.
2. **Voice Activity Detection**: `_detect_speech(temp_wav_path)` -> Uses `silero-vad` to return speech timestamps strictly mapped to **milliseconds**.
3. **FFmpeg Video Generation**: `_apply_ffmpeg_jump_cut(video_path, output_path, timestamps)` -> Calculates float-seconds internally, generates FFmpeg filter strings (`select`, `aselect`, `setpts`, `asetpts`) and outputs the optimized video.

## Data Flow
1. **Client -> Server**: MCP invocation `jump_cut_video` with `video_path` and `audio_path`.
2. **Tool -> Logic**: Tool converts parameters to `JumpCutRequest` and calls `process_jump_cut()`.
3. **Logic (VAD)**: Validates both files, extracts 16kHz audio, runs model, returning standard `[start_ms, end_ms]`.
4. **Logic (FFmpeg)**: Converts mappings from ms to seconds for the subprocess wrapper `ffmpeg-python`.
5. **Logic -> Tool**: `process_jump_cut()` returns a `JumpCutResponse`.
6. **Server -> Client**: Tool returns the processed video path string.

## Edge Cases
- **No speech detected**: The handler throws a domain-specific `ValueError` before calling FFmpeg.
- **Model Loading Delay**: The Silero VAD model is loaded dynamically only when the use case is invoked.
