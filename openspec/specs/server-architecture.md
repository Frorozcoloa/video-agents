# Server Architecture Specification

## Overview
This specification defines the communication transport and network configuration for the Video Agents MCP Server.

## Transport Configuration
The server is configured to use **HTTP (SSE)** as its primary transport method to allow for broader client compatibility (Postman, Curl, custom HTTP clients) beyond standard `stdio` environments.

### Protocol
- **Transport Type**: Server-Sent Events (SSE) / `streamable-http`.
- **Port**: `8000` (Default FastMCP port).
- **Format**: JSON-RPC 2.0.

### Endpoints
- `GET /sse`: Establishes the event stream connection and provides a unique `session_id`.
- `POST /messages?session_id=<ID>`: Endpoint for sending JSON-RPC commands (tools/list, tools/call, etc.).

## Docker Integration
The server is containerized to ensure consistent environments and easy deployment.

### Container Configuration
- **Base Image**: `python:3.12-slim`.
- **Dependencies**: Includes `ffmpeg` for media processing.
- **Exposure**: Port `8000` must be mapped to the host for external access.
- **Environment Variables**:
  - `MCP_TRANSPORT`: Can be used to override the default transport (currently fixed to `http` in `src/server.py` for this spec).

## Client Interactivity
### Postman / Curl
- Clients must maintain an open `GET` connection to `/sse` to receive asynchronous responses.
- All commands are sent via `POST` to the session-specific message endpoint.
