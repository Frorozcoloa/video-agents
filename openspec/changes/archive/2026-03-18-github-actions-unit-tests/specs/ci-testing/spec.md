## ADDED Requirements

### Requirement: Automated Trigger on Commits and Pull Requests
The system SHALL automatically trigger a unit test workflow whenever a commit is pushed to the `main` branch OR a Pull Request is created or updated targeting the `main` branch.

#### Scenario: Commit pushed to main
- **WHEN** a developer pushes a commit directly to the `main` branch
- **THEN** the GitHub Actions workflow "Unit Tests" SHALL start execution.

#### Scenario: PR from feature branch to main
- **WHEN** a Pull Request is opened from `feature/new-feature` to `main`
- **THEN** the GitHub Actions workflow "Unit Tests" SHALL start execution.
