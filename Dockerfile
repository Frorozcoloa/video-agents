# Use Python slim image for the build stage
FROM python:3.12-slim AS builder

# Install uv and git (needed for git+ dependencies like toon-format)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Sync dependencies (allowing CPU-based resolution)
RUN uv sync --frozen --no-install-project

# Use Python slim image for the final stage
FROM python:3.12-slim

# Install system dependencies (ffmpeg is still required for media)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy source code
COPY src/ /app/src/

# Healthcheck to verify the server process is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python src/server.py" || exit 1

# Default command
ENTRYPOINT ["python", "src/server.py"]
