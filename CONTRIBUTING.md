# Contributing to TimeRun

Thank you for considering contributing to TimeRun. This guide explains how to set up your environment, run tests, and submit changes.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How You Can Help](#how-you-can-help)
- [Development Setup](#development-setup)
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

## Development Setup

### Prerequisites

- **Python 3.9+**
- **Git**

### One-time setup

1. **Fork** the repository on GitHub, then clone your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/timerun.git
   cd timerun
   ```

2. **Create and activate a virtual environment** (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install the project in editable mode with dev dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install and enable pre-commit hooks** (optional but recommended):

   ```bash
   pip install pre-commit
   pre-commit install
   ```

   Or use the convenience target:

   ```bash
   make init
   ```

   Then activate the venv: `source .venv/bin/activate`.

### Verify setup

Run the test suite:

```bash
make test
```

You should see the BDD scenarios run and a coverage report.

## Testing

TimeRun uses **behavior-driven development (BDD)** with [behave](https://behave.readthedocs.io/). All tests are written in Gherkin and live under `features/`.

### Run tests

| Command        | Description                          |
|----------------|--------------------------------------|
| `make test`    | Run BDD suite with coverage report   |
| `behave`       | Run BDD suite only (no coverage)     |

### Run coverage manually

```bash
coverage run --source=timerun -m behave
coverage report --show-missing
```

### Adding or changing tests

- **Feature files** — Add or edit `.feature` files in `features/` (e.g. `features/version.feature`). Use standard Gherkin: `Feature`, `Scenario`, `Given`, `When`, `Then`.
- **Step definitions** — Implement steps in Python under `features/steps/`, typically in a `*_steps.py` file. Use `@given`, `@when`, `@then` from `behave`; step functions receive a `context` argument.
- Keep scenarios focused and steps reusable. Add or extend scenarios for new behavior rather than skipping BDD.

## Code Style and Quality

Style and linting are enforced via **pre-commit** (Ruff, mypy, Pylint, and other hooks). After `pre-commit install`, these run automatically on each commit.

### Run checks manually

```bash
pre-commit run --all-files
```

### What we expect

- **Formatting** — Ruff format (run via pre-commit or `ruff format`).
- **Linting** — Ruff check, Pylint, and other hooks must pass.
- **Types** — Use type hints for public APIs; mypy must pass.
- **Docstrings** — Public functions, classes, and modules should have docstrings.
- **Security** — Bandit and Semgrep run in pre-commit; address any reported issues.

Fixing pre-commit failures before pushing keeps the history clean and CI green.

## Project Structure

```
timerun/
├── timerun.py          # Library (single-file by design)
├── features/            # BDD feature files (Gherkin)
│   ├── *.feature
│   └── steps/           # Step definitions (Python)
│       └── *_steps.py
├── pyproject.toml       # Project metadata and config
├── Makefile             # Commands: init, test, clean, help
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

- **`timerun.py`** — The only library module; keep it a single file by design.
- **`features/`** — All executable specs; no separate unit test directory.

## Pull Request Process

1. **Create a branch** from `main`:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/short-description   # or fix/short-description
   ```

2. **Make your changes** — Follow [Code Style and Quality](#code-style-and-quality) and add or update BDD scenarios in `features/` for new or changed behavior.

3. **Run the suite and pre-commit**:

   ```bash
   make test
   pre-commit run --all-files
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
