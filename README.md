# Video Agents

MCP Server for automated video and audio editing with AI.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)
- FFmpeg (for media processing)
- Docker (optional)

## Connecting with Gemini CLI (HTTP/SSE)

The server is configured to run on **HTTP** (SSE) on port **8000**. To connect it to **Gemini CLI**, add the following configuration to your `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "video-agents": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Running the Server

Before connecting, you must have the server running:

```bash
uv run src/server.py
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

## Testing with Curl (SSE)

Como el servidor usa **Server-Sent Events (SSE)**, necesitas dos pasos:

1.  **Escuchar eventos**:
    ```bash
    curl -N http://localhost:8000/sse
    ```
    *Copia el `session_id` del mensaje inicial.*

2.  **Enviar comando (POST)**:
    ```bash
    curl -X POST "http://localhost:8000/messages?session_id=TU_SESSION_ID" \
         -H "Content-Type: application/json" \
         -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
    ```

## Connecting with Postman

1.  **Connect**: Nuevo request `GET` a `http://localhost:8000/sse` y clic en **Connect**.
2.  **Command**: En una nueva pestaña, crea un request `POST` a la URL con el `session_id` obtenido.
3.  **Result**: Los resultados aparecerán en la primera pestaña (la del `GET /sse`).
