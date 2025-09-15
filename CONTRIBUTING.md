# Contributing to TimeRun

Thank you for your interest in contributing to TimeRun! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/timerun.git
   cd timerun
   ```

3. Set up the development environment:
   ```bash
   make init
   ```

4. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Development Workflow

### Running Tests

Run the test suite with coverage:
```bash
make test
```

### Code Style

This project follows these code style guidelines:
- **Black** for code formatting (line length: 79 characters)
- **isort** for import sorting

Pre-commit hooks are installed automatically with `make init` and will run on every commit. You can also run them manually:
```bash
pre-commit run --all-files
```

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the project conventions
3. Add or update tests as needed
4. Ensure all tests pass: `make test`
5. Commit your changes with a clear message

### Submitting Changes

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request on GitHub with:
   - Clear description of the changes
   - Reference to any related issues
   - Test coverage for new functionality

## Project Structure

- `timerun.py` - Main library code (single file module)
- `tests/` - Test suite
- `pyproject.toml` - Project configuration and dependencies
- `Makefile` - Development commands

## Guidelines

### Code Quality

- Maintain 100% test coverage for new code
- Follow existing code patterns and conventions
- Add docstrings for all public functions and classes
- Use type hints consistently

### Testing

- Write tests for all new functionality
- Use descriptive test names
- Test both success and error cases
- Keep tests focused and independent

### Documentation

- Update docstrings for any API changes
- Add examples for new features
- Update README.md if needed

## Reporting Issues

When reporting bugs or requesting features:

1. Check existing issues first
2. Use the issue templates if available
3. Provide clear reproduction steps for bugs
4. Include Python version and environment details

## Questions?

Feel free to open an issue for questions about contributing or reach out to the maintainers.

## License

By contributing to TimeRun, you agree that your contributions will be licensed under the MIT License.
