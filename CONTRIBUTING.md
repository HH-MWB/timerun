# Contributing to TimeRun

Thank you for considering contributing to TimeRun. This guide explains how to set up your environment, run tests, and submit changes.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How You Can Help](#how-you-can-help)
- [Setup](#setup)
- [Development Commands](#development-commands)
- [Testing](#testing)
- [Code Style and Quality](#code-style-and-quality)
- [Project Structure](#project-structure)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [License](#license)

## Code of Conduct

Please be respectful and constructive. By participating, you agree to uphold a welcoming environment for everyone.

## How You Can Help

- **Report bugs** — Open an issue with clear steps to reproduce.
- **Suggest features** — Open an issue describing the use case and desired behavior.
- **Submit code** — Fix bugs or add features via pull requests (see [Pull Request Process](#pull-request-process)).
- **Improve docs** — Fix typos, clarify README or docstrings, or add examples.

## Setup

### Prerequisites

- **Python 3.10+**
- **Git**

### One-time setup

1. Fork the repository on GitHub, then clone your fork and go into the project directory:

   ```bash
   git clone https://github.com/YOUR_USERNAME/timerun.git
   cd timerun
   ```

2. Run `make init`. This creates a `.venv`, installs the package in editable mode with dev dependencies, and installs pre-commit hooks.

3. Optionally activate the venv for interactive use: `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`). You can run `make test` and `make lint` without activating.

### Verify setup

1. Run `make test`. You should see the BDD scenarios run and a coverage report.
2. Run `make lint`. Lint should pass.

## Development Commands

Use the Makefile for common tasks. Run `make help` for the full list.

- **`make help`** — Show all targets and descriptions
- **`make init`** — Set up venv, install package and dev deps, install pre-commit hooks
- **`make test`** — Run BDD tests with coverage (summary output)
- **`make test-verbose`** — Run BDD tests with full scenario/step output (for debugging)
- **`make lint`** — Run pre-commit (format and lint) on all files
- **`make clean`** — Remove venv, caches, and build artifacts

## Testing

TimeRun uses **behavior-driven development (BDD)** with [behave](https://behave.readthedocs.io/). All tests are written in Gherkin and live under `features/`.

### Run tests

- Use **`make test`** for normal runs (summary and coverage; failures show which scenario failed).
- Use **`make test-verbose`** when debugging failures (full scenario/step output).

### Adding or changing tests

- **Feature files** — Add or edit `.feature` files in `features/` (e.g. `features/version.feature`). Use standard Gherkin: `Feature`, `Scenario`, `Given`, `When`, `Then`.
- **Step definitions** — Implement steps in Python under `features/steps/`, typically in a `*_steps.py` file. Use `@given`, `@when`, `@then` from `behave`; step functions receive a `context` argument.
- Keep scenarios focused and steps reusable. Add or extend scenarios for new behavior rather than skipping BDD.

## Code Style and Quality

Pre-commit hooks (installed by `make init`) run on each commit. Before pushing, run `make lint` and fix any failures so CI stays green.

We expect (all run via `make lint`):

- **pre-commit-hooks** — Trailing whitespace removed, end-of-file newline, no BOM, LF line endings; YAML and TOML syntax checked
- **Ruff** — Code formatting (`ruff-format`) and linting (`ruff-check`)
- **mypy** — Static type checking on `timerun.py`; use type hints on public APIs
- **Pylint** — Lint and style on `timerun.py`; docstrings expected on public functions, classes, and modules
- **Bandit** — Security issue detection (config in `pyproject.toml`)
- **Semgrep** — Security and bug patterns (Python ruleset)
- **yamllint** — YAML style and syntax (e.g. workflow and config files)

## Project Structure

```
timerun/
├── timerun.py          # Library (single-file by design)
├── features/            # BDD feature files (Gherkin) — behave convention
│   ├── __init__.py      # Makes features a package for imports
│   ├── *.feature
│   ├── environment.py  # Optional: hooks (before/after scenario, etc.)
│   └── steps/           # Step definitions (flat; all .py files loaded)
│       ├── __init__.py
│       ├── utils.py         # Shared constants and helpers (no step decorators)
│       ├── common_steps.py  # Shared steps used by multiple features
│       └── *_steps.py       # Feature-specific step files
├── pyproject.toml       # Project metadata and config
├── Makefile             # Commands: init, check-venv, test, test-verbose, lint, clean, help
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

- **`timerun.py`** — The only library module; keep it a single file by design.
- **`features/`** — All executable specs; no separate unit test directory. Layout follows [behave](https://behave.readthedocs.io/) convention: step definitions live under `features/steps/` (flat; subdirectories are not searched). Shared logic lives in `features/steps/utils.py`; shared steps (e.g. metadata, wall-time buffer, exception propagation) in `common_steps.py`. Run behave from the project root so `from features.steps.utils import ...` works.

## Pull Request Process

1. **Create a branch** from `main`:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/short-description   # or fix/short-description
   ```

2. **Make your changes** — Follow [Code Style and Quality](#code-style-and-quality) and add or update BDD scenarios in `features/` for new or changed behavior.

3. **Verify lint and tests pass** (run lint, then tests):

   ```bash
   make lint test
   ```

4. **Commit** with clear, concise messages. Optionally use conventional style (e.g. `feat: add X`, `fix: correct Y`).

5. **Push** to your fork and open a pull request against `main`:

   ```bash
   git push origin feature/short-description
   ```

6. **Fill out the PR**:
   - Describe what changed and why.
   - Reference any related issues (e.g. "Fixes #123").
   - Confirm tests pass and, for new behavior, that BDD scenarios were added or updated.

Maintainers will review and may request changes. Once approved, your PR will be merged.

## Reporting Bugs

- **Search** existing issues to avoid duplicates.
- **Open an issue** with:
  - A short, clear title.
  - Steps to reproduce (code or commands).
  - Expected vs actual behavior.
  - Your environment: OS, Python version (`python --version`), and how you installed TimeRun (pip, editable, etc.).

For small, obvious fixes you may open a PR directly with a short explanation.

## License

Contributions are made under the [MIT License](LICENSE). By submitting a pull request, you agree that your contributions will be licensed under the same terms.
