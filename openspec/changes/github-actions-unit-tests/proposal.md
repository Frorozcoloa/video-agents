## Why

To maintain high code quality and prevent regressions, we need an automated CI/CD pipeline that runs unit tests whenever a Pull Request is created from a feature branch to the master branch. This ensures that only verified code is merged.

## What Changes

- Add a new GitHub Actions workflow file at `.github/workflows/unit-tests.yml`.
- Configure the workflow to trigger on `pull_request` events targeting the `master` branch from `feature/*` branches.
- The workflow will install dependencies using `uv` and run `pytest`.

## Capabilities

### New Capabilities
- `ci-testing`: Automated execution of unit tests in GitHub Actions environment.

### Modified Capabilities
<!-- Existing capabilities whose REQUIREMENTS are changing (not just implementation).
     Only list here if spec-level behavior changes. Each needs a delta spec file.
     Use existing spec names from openspec/specs/. Leave empty if no requirement changes. -->

## Impact

- **CI/CD Pipeline**: Introduction of GitHub Actions.
- **Development Workflow**: Developers will see automated test results on their Pull Requests.
