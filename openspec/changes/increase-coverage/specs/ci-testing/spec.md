## MODIFIED Requirements

### Requirement: Code Coverage Report
The workflow SHALL calculate code coverage using `pytest-cov`, display the report in the workflow summary, and save the XML report as a build artifact. The build SHALL fail if the total coverage is below 80%.

#### Scenario: Coverage below 80% (Improved)
- **WHEN** the unit tests pass but the total code coverage is less than 80%
- **THEN** the GitHub Action status SHALL be marked as failed.
- **AND** the system SHALL provide a detailed report of missing lines in `src/server.py` and other files with coverage below 70%.

#### Scenario: Coverage 80% or above
- **WHEN** the unit tests pass and the total code coverage is 80% or more
- **THEN** the GitHub Action status SHALL be marked as successful.
