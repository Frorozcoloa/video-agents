# Video Agents

MCP Server for automated video and audio editing with AI.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)
- FFmpeg (for media processing)
- Docker (optional)

## Running the Server (HTTP Mode)

Por defecto, el servidor está configurado para correr en modo **HTTP** en el puerto **8000**. Esto permite conexiones externas (Postman, Curl, etc.) y es el estándar para `fastmcp`.

### Local con `uv`

```bash
uv run src/server.py
```

### Running with Docker

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
