# Continuous Integration (CI) Testing Specification

## Requirements

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

### Requirement: Code Coverage Report
The workflow SHALL calculate code coverage using `pytest-cov`, display the report in the workflow summary, and save the XML report as a build artifact. The build SHALL fail if the total coverage is below 80%.

#### Scenario: Coverage below 80%
- **WHEN** the unit tests pass but the total code coverage is less than 80%
- **THEN** the GitHub Action status SHALL be marked as failed.
- **AND** the system SHALL provide a detailed report of missing lines in `src/server.py` and other files with coverage below 70%.

#### Scenario: Coverage 80% or above
- **WHEN** the unit tests pass and the total code coverage is 80% or more
- **THEN** the GitHub Action status SHALL be marked as successful.
