## 1. Setup

- [x] 1.1 Create the `.github/workflows/` directory if it does not exist.

## 2. Workflow Implementation

- [x] 2.1 Create `.github/workflows/unit-tests.yml` with the specified triggers (PR to `master` from `feature/*`).
- [x] 2.2 Configure the job to use `ubuntu-latest` and Python 3.12.
- [x] 2.3 Add a step to install `uv` (using `astral-sh/setup-uv`).
- [x] 2.4 Add a step to sync project dependencies (`uv sync`).
- [x] 2.5 Add a step to execute tests using `pytest`.

## 3. Verification

- [x] 3.1 Verify the YAML syntax of the new workflow file.
- [x] 3.2 Ensure the workflow is correctly recognized by GitHub.
- [x] 3.3 (Optional) Trigger a dummy Pull Request from a feature branch to `master` to confirm the workflow starts and runs correctly.
