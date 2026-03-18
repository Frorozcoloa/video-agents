## ADDED Requirements

### Requirement: Automated Trigger on Pull Requests
The system SHALL automatically trigger a unit test workflow whenever a Pull Request is created or updated targeting the `main` branch from any branch starting with `feature/`.

#### Scenario: PR from feature branch to main
- **WHEN** a Pull Request is opened from `feature/new-feature` to `main`
- **THEN** the GitHub Actions workflow "Unit Tests" SHALL start execution.

### Requirement: Test Environment Setup
The workflow SHALL set up a Python 3.12 environment and install all project dependencies using `uv` before running the tests.

#### Scenario: Successful environment setup
- **WHEN** the workflow starts
- **THEN** it SHALL install `uv`, sync dependencies from `uv.lock`, and ensure Python 3.12 is used.

### Requirement: Unit Test Execution
The workflow SHALL execute the test suite using `pytest` and report the results back to the Pull Request.

#### Scenario: Tests pass
- **WHEN** all unit tests in the `tests/` directory pass
- **THEN** the GitHub Action status SHALL be marked as successful.

#### Scenario: Tests fail
- **WHEN** any unit test in the `tests/` directory fails
- **THEN** the GitHub Action status SHALL be marked as failed, preventing the PR from being considered "clean".
