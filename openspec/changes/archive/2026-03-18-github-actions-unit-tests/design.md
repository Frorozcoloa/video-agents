## Context

The project currently lacks an automated continuous integration (CI) pipeline to verify code changes. Developers must run tests manually before pushing, which is error-prone and can lead to broken code in the `main` branch.

## Goals / Non-Goals

**Goals:**
- Automate unit test execution on Pull Requests from `feature/*` to `main`.
- Provide immediate feedback to developers on GitHub.
- Use the existing `uv` package manager for consistent environment setup.

**Non-Goals:**
- Deployment automation (CD).
- Integration tests or performance benchmarks (out of scope for this initial setup).
- Linting or type checking (will be added in future iterations).

## Decisions

- **CI Provider**: GitHub Actions. Rationale: Native integration with the repository and free for public/standard private repos.
- **Environment**: `ubuntu-latest`. Rationale: Standard, stable, and widely supported environment for Python projects.
- **Python Version**: 3.12. Rationale: Matches the project's `.python-version` and `pyproject.toml` requirements.
- **Package Manager**: `uv`. Rationale: Significantly faster than `pip` and already used in the project for dependency management.
- **Test Runner**: `pytest`. Rationale: The established test framework in the project.

## Risks / Trade-offs

- **[Risk] Slow Execution** → Media processing dependencies (like FFmpeg or large AI models) can make CI runs slow. **Mitigation**: We will only run unit tests, which should mock heavy dependencies where possible.
- **[Trade-off] complexity vs Speed** → Using `uv` adds a setup step but provides faster installs and better reproducibility compared to standard `pip`.
