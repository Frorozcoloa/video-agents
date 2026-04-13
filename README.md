# Video Agents

MCP Server for automated video and audio editing with AI.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)
- FFmpeg (for media processing)
- Docker (optional)

## Connecting with Gemini CLI (HTTP)

The server runs on **HTTP** transport on port **8000**, endpoint `/mcp`. To connect it to **Gemini CLI**, add the following configuration to your `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "video-agents": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Running the Server

Before connecting, you must have the server running:

```bash
uv run fastmcp run src/server.py --transport http --host 0.0.0.0 --port 8000
```

## Running the Server with Docker

#### 1. Build the image
```bash
docker build -t video-agents .
```

#### 2. Run the container
```bash
docker run -p 8000:8000 video-agents
```

## Testing with Curl

Send a JSON-RPC request directly to the `/mcp` endpoint:

```bash
curl -X POST "http://localhost:8000/mcp" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## Connecting with Postman

1.  **Send a command**: Create a `POST` request to `http://localhost:8000/mcp`.
2.  **Set headers**: `Content-Type: application/json`.
3.  **Set body**: A JSON-RPC 2.0 payload, e.g. `{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}`.
4.  **View results**: The response will appear in the response panel.

## Available Tools

All timestamps are in **milliseconds**. Responses use TOON format (compact LLM-friendly encoding) unless otherwise noted.

### `extract_audio`
Extracts high-quality audio from a video file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_path` | str | yes | Path to the input video file |
| `output_path` | str | no | Output path for the audio file (default: derived from input) |

Returns: path to the extracted audio file.

---

### `transcribe_audio`
Transcribes an audio file and returns text with millisecond timestamps using faster-whisper.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio_path` | str | yes | Path to the audio file (.mp3, .wav, etc.) |
| `model_size` | str | no | Whisper model size: `base` (default), `small`, `medium` |

Returns: TOON-encoded transcription with word-level timestamps.

---

### `clip_video`
Clips a segment from a video file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_path` | str | yes | Path to the input video file |
| `start_time` | int | yes | Start timestamp in milliseconds |
| `end_time` | int | yes | End timestamp in milliseconds |
| `output_path` | str | no | Output path for the clipped video |
| `mode` | str | no | `fast` (keyframe-accurate streamcopy, default) or `exact` (frame-accurate re-encode) |

Returns: path to the clipped video file.

---

### `jump_cut_video`
Removes silences automatically using Silero VAD to create a jump-cut edit.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_path` | str | yes | Path to the input video file |
| `audio_path` | str | yes | Path to the extracted audio file for silence detection |
| `output_path` | str | no | Output path for the result |

Returns: path to the jump-cut video file.

---

### `apply_broll`
Overlays a B-roll clip onto a time-bounded segment of the main video. B-roll is scaled to match main video dimensions; main audio is preserved.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_path` | str | yes | Path to the main video file |
| `broll_path` | str | yes | Path to the B-roll clip |
| `start_ms` | int | yes | Overlay start timestamp in milliseconds |
| `end_ms` | int | yes | Overlay end timestamp in milliseconds |
| `output_path` | str | no | Output path (default: input with `_broll` suffix) |

Returns: TOON-encoded result with `output_path`.

---

### `audio_ducking`
Mixes a voice track over background music with automatic sidechain ducking — music volume is reduced whenever the voice is active.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `voice_path` | str | yes | Path to the voice/voiceover audio file |
| `music_path` | str | yes | Path to the background music audio file |
| `output_path` | str | yes | Path for the mixed output audio file |
| `threshold` | float | no | Compression threshold 0.0–1.0 (default `0.1`) |
| `ratio` | float | no | Compression ratio ≥1.0 (default `5.0`) |
| `attack` | int | no | Attack time in ms ≥1 (default `20`) |
| `release` | int | no | Release time in ms ≥1 (default `500`) |

Returns: TOON-encoded result with `output_path` and applied params.

---

### `mix_audio_segments`
Places timed audio clips into a video, mixing or replacing the original audio. Video stream is copied without re-encoding.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_path` | str | yes | Path to the input video file |
| `segments` | list[dict] | yes | List of `{audio_path, start_ms, end_ms}` objects |
| `output_path` | str | no | Output path (default: input with `_mixed` suffix) |
| `replace_original` | bool | no | If `true`, silence original audio and use only segments (default `false`) |

Returns: TOON-encoded result with `output_path` and `segments_count`.

---

### Resource: `video://{video_path}/scenes`
Detects scene boundaries in a video using PySceneDetect's ContentDetector.

| Parameter | Type | Description |
|-----------|------|-------------|
| `video_path` | str | Absolute path to the video file |

Returns: TOON-encoded list of scenes with `start_ms` and `end_ms` timestamps.
