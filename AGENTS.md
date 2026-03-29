# AGENTS.md

This file defines guidelines and standard operating procedures for autonomous AI agents contributing to the `video-agents` project.
For more information about `AGENTS.md`, visit [agents.md](https://agents.md/).

## 🎯 Golden Rules
1. **NEVER SKIP PRE-COMMITS.** Pre-commits are mandatory to ensure code quality and formatting. Do not use `--no-verify` when committing. If pre-commits fail, you must fix the issues and try again.
2. Ensure you have activated the environment with `uv` or use `uv run <command>`.
3. Use `uv sync` to manage dependencies. `uv add` for new dependencies.

## 🏗️ Architecture
- This project is an MVP/MCP (Model Context Protocol) Server for automated video and audio editing powered by AI.
- **Entry Point**: `src/server.py` defines the MCP Server.
- **Modular Features**: Tools are encapsulated by domain within the `src/features/` directory:
  - `audio_extraction/`
  - `audio_transcription/`
  - `video_clipping/`
- **Output Standardization**: Tools use the `toon-format` protocol wrapper to optimize responses for LLMs.

## 🛠️ Technologies
- **Runtime**: Python 3.12+
- **Environment & Dependencies**: `uv`
- **MCP Framework**: `fastmcp[tasks]`
- **Media Processing**: `ffmpeg-python`, `scenedetect` (OpenCV enabled)
- **AI/ML Utilities**: `faster-whisper` (transcription), `silero-vad` (voice activity), `torch`, `onnxruntime`
- **Data Validation**: `pydantic`
- **Formatting and Linting**: `ruff` (likely handled by `pre-commit`)

## 🧪 Executing Unit Tests
To run unit tests and check test coverage, run:
```bash
uv run pytest
```
Testing enforces an 80% minimum coverage. If you write new code, you MUST adapt or write new test cases inside the `tests/` directory to meet this threshold.

## 📝 Pre-commit Workflow
When you are ready to commit changes:
1. Stage your changes: `git add .`
2. Run pre-commit checks: `uv run pre-commit run --all-files` (or simply run `git commit` and let the hook run).
3. If pre-commit reformats files (e.g., via `ruff`), stage the newly modified files again: `git add .`
4. Commit. Do NOT bypass the hook!
