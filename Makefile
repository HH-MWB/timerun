# Makefile for Timerun
# Description: Development environment setup and project management
# Requirements: Python 3, pip

.DEFAULT_GOAL := help

# Project configuration
VENV_DIR := .venv

.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

.PHONY: init
init: ## Set up Python development environment
	@test -d "$(VENV_DIR)" || python3 -m venv "$(VENV_DIR)" >/dev/null 2>&1
	@"$(VENV_DIR)/bin/pip" install -e ".[dev]" >/dev/null 2>&1
	@echo "Development environment ready! To activate it, run: source $(VENV_DIR)/bin/activate"

.PHONY: test
test: ## Run all tests and display coverage ratio
	@"$(VENV_DIR)/bin/pytest" tests/ --cov=timerun --cov-report=term-missing

.PHONY: clean
clean: ## Delete all temporary files including venv
	@rm -rf "$(VENV_DIR)" *.egg-info
	@rm -rf .mypy_cache .pytest_cache .coverage htmlcov
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} +
