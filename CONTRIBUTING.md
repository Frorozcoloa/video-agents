# Contributing to Video Agents

We follow the **Ship, Show, Ask** branching and contribution workflow.

## Ship, Show, Ask

### 🛳️ Ship
Small, low-risk changes that can be merged directly into the main branch without review.
- Documentation fixes.
- Minor bug fixes with existing test coverage.
- Project initialization tasks.

### 👓 Show
Changes that are ready to be merged but would benefit from visibility.
- New features following the Vertical Slice Architecture (VSA).
- Refactoring that improves code quality without changing behavior.
- Use a Pull Request and merge immediately after automated tests pass.

### ❓ Ask
Major changes that require discussion and review before merging.
- Architectural changes.
- Large feature additions.
- Changes that affect the Project Constitution.
- Use a Pull Request and wait for approval.

## Engineering Standards
- **Spec-Driven Development (SDD)**: Define specs before implementing.
- **Vertical Slice Architecture (VSA)**: Keep features self-contained in `src/features/`.
- **Validation**: Use strict Pydantic models.
- **Asynchronicity**: Ensure media tasks do not block the main loop.
