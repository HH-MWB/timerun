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
- [Releasing](#releasing)
- [Reporting Bugs](#reporting-bugs)
- [License](#license)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/3/0/). See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the full text and how to report issues.

## How You Can Help

- **Report bugs** — Open an issue with clear steps to reproduce.
- **Suggest features** — Open an issue describing the use case and desired behavior.
- **Submit code** — Fix bugs or add features via pull requests (see [Pull Request Process](#pull-request-process)).
- **Improve docs** — Fix typos, clarify README or docstrings, or add examples.

## Setup

### Prerequisites

- **Python 3.10+**
- **pip** (usually bundled with Python)
- **Make**
- **Git**

### One-time setup

1. Fork the repository on GitHub, then clone your fork and go into the project directory:

   ```bash
   git clone https://github.com/YOUR_USERNAME/timerun.git
   cd timerun
   ```

2. Run `make init`. You will be prompted to choose a Python interpreter (press Enter for `python3`, or type e.g. `python3.10`). To skip the prompt, run `make init PYTHON=python3.10` (or another 3.10+ interpreter). This creates a `.venv`, installs the package in editable mode with dev and docs dependencies (Zensical), and installs pre-commit hooks.

3. Optionally activate the venv for interactive use: `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`). You can run `make test` and `make lint` without activating.

### Verify setup

1. Run `make test`. You should see the BDD scenarios run and a coverage report.
2. Run `make lint`. Lint should pass.

## Development Commands

Use the Makefile for common tasks. Run `make help` for the full list.

- **`make help`** — Show all targets and descriptions
- **`make init`** — Prompts for Python interpreter (default: `python3`); set `PYTHON` to skip (e.g. `make init PYTHON=python3.10`). Sets up venv, installs package and dev + docs deps (Zensical), installs pre-commit hooks.
- **`make clean`** — Remove all files and directories listed in `.gitignore` (inverse of init)
- **`make test`** — Run BDD tests with coverage (summary output)
- **`make test-verbose`** — Run BDD tests with full scenario/step output (for debugging)
- **`make docs`** — Serve the docs locally (http://127.0.0.1:8000)
- **`make docs-build`** — Build the docs site (output in `site/`; config: `zensical.toml`)
- **`make lint`** — Run pre-commit (format and lint) on all files

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

CI (on pull requests and pushes to `main`) runs: **lint** (pre-commit) → **test** (Python 3.10–3.14 matrix, with coverage) → **build** (package build and `twine check`). Outdated runs for the same branch are cancelled automatically.

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
├── .editorconfig             # Editor configuration for consistent style across editors
├── .github/                  # GitHub configuration
│   ├── ISSUE_TEMPLATE/       # Issue templates (bug report, feature request)
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/            # CI (ci.yaml), pages (pages.yaml), release (release.yaml)
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── features/                 # BDD feature files (Gherkin) — behave convention
│   ├── *.feature
│   ├── __init__.py
│   ├── environment.py        # Optional: hooks (before/after scenario, etc.)
│   └── steps/                # Step definitions (flat; all .py files loaded)
│       ├── __init__.py
│       ├── common_steps.py   # Shared steps used by multiple features
│       └── *_steps.py        # Feature-specific step files
├── pyproject.toml            # Project metadata and config
├── zensical.toml             # Docs site config (Zensical)
├── docs/                     # Docs source (Markdown)
├── timerun.py                # Library (single-file by design)
├── Makefile                  # Commands: init, test, test-verbose, lint, docs, docs-build, clean, help
├── README.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
└── SECURITY.md
```

- **`timerun.py`** — The only library module; keep it a single file by design.
- **`features/`** — All executable specs; no separate unit test directory. Layout follows [behave](https://behave.readthedocs.io/) convention: step definitions live under `features/steps/` (flat; subdirectories are not searched). Shared steps (e.g. metadata, wall-time buffer, exception propagation) live in `common_steps.py`. Run behave from the project root.

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

## Releasing

Releases are driven by **GitHub Releases** and publish to **TestPyPI** first, then **PyPI** after confirmation.

### Prerequisites (maintainers)

- **Environments** in this repo: `testpypi` and `pypi` (Settings → Environments).
- **Trusted Publishing** configured on [PyPI](https://pypi.org/manage/account/publishing/) and [TestPyPI](https://test.pypi.org/manage/account/publishing/) for this repository, workflow `release.yaml`, and the corresponding environment names.

### Release flow

1. **Bump version** in `timerun.py` (`__version__`) and commit to `main`.
2. **Create a GitHub Release** (Releases → Draft a new release):
   - Choose or create a tag (e.g. `v1.0.0`) from `main`.
   - Check **“This is a pre-release”**.
   - Add release notes and publish.
3. The **release workflow** runs and publishes the package to **TestPyPI** only.
4. **Test** the package from TestPyPI (e.g. `pip install -i https://test.pypi.org/simple/ timerun==1.0.0`).
5. When satisfied, **edit the release** on GitHub: uncheck “This is a pre-release” and save.
6. The workflow runs again and publishes to **PyPI**.

The same workflow handles both events: `release: types: [published, edited]`. Pre-release → TestPyPI; full release → PyPI.

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
