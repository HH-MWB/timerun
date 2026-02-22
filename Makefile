# TimeRun - Makefile
#
# This Makefile provides convenient commands for development environment setup,
# testing, linting, and project management. Requirements: Python 3.10+, pip.
#
# Usage:
#   make [target]
#   make help          # Display available targets and descriptions

# ============================================================================
# Configuration (edit only the "Editable" block if needed)
# ============================================================================

# Editable: change these to match your environment
VENV_DIR := .venv
PYTHON := python3

# Derived: do not edit (computed from above or project layout)
VENV_BIN := $(VENV_DIR)/bin
CLEAN_RM := $(VENV_DIR) .mypy_cache .ruff_cache .coverage htmlcov site
CLEAN_GLOB := *.egg-info
COVERAGE_SOURCE := timerun

# Default target when no target is specified
.DEFAULT_GOAL := help

# ============================================================================
# General Targets
# ============================================================================

##@ General

.PHONY: help
help: ## Display this help message with all available targets
	@echo "TimeRun - Available Commands"
	@echo ""
	@echo "Usage: make [target]"
	@awk 'BEGIN {FS = ":.*##"} \
		/^[a-zA-Z_0-9-]+:.*?##/ { \
			printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 \
		} \
		/^##@/ { \
			printf "\n\033[1m%s\033[0m\n", substr($$0, 5) \
		}' $(MAKEFILE_LIST)

# ============================================================================
# Environment Targets
# ============================================================================

##@ Environment

.PHONY: init
init: ## Set up Python development environment (dev + docs deps) and pre-commit hooks
	@echo "Setting up TimeRun development environment..."
	@test -d "$(VENV_DIR)" || $(PYTHON) -m venv "$(VENV_DIR)" >/dev/null 2>&1
	@$(VENV_BIN)/pip install -e ".[dev,docs]" >/dev/null 2>&1
	@$(VENV_BIN)/pip install pre-commit >/dev/null 2>&1
	@$(VENV_BIN)/pre-commit install >/dev/null 2>&1

.PHONY: check-venv
check-venv: ## Ensure virtual environment exists and timerun is installed (internal)
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Error: $(VENV_DIR) not found!"; \
		echo "Please run 'make init' to create the development environment."; \
		exit 1; \
	fi
	@if ! $(VENV_BIN)/python -c "import timerun" 2>/dev/null; then \
		echo "Error: timerun not installed in $(VENV_DIR)!"; \
		echo "Please run 'make init' to install the package and dependencies."; \
		exit 1; \
	fi

# ============================================================================
# Testing Targets
# ============================================================================

##@ Testing

# BEHAVE_ARGS set per target: -f null for quiet, empty for verbose
.PHONY: test
test: BEHAVE_ARGS := -f null
test: check-venv ## Run BDD tests (summary + coverage; failures show which scenario failed)
	@$(VENV_BIN)/coverage run --source=$(COVERAGE_SOURCE) -m behave $(BEHAVE_ARGS)
	@$(VENV_BIN)/coverage report --show-missing

.PHONY: test-verbose
test-verbose: BEHAVE_ARGS :=
test-verbose: check-venv ## Run BDD tests with full scenario/step output (for debugging failures)
	@$(VENV_BIN)/coverage run --source=$(COVERAGE_SOURCE) -m behave $(BEHAVE_ARGS)
	@$(VENV_BIN)/coverage report --show-missing

# ============================================================================
# Docs Targets (Zensical; docs deps installed by make init)
# ============================================================================

##@ Docs

.PHONY: docs
docs: check-venv ## Serve the docs locally (http://127.0.0.1:8000); Ctrl+C removes site/
	@trap 'rm -rf site' INT; $(VENV_BIN)/zensical serve

.PHONY: docs-build
docs-build: check-venv ## Build the docs site (output in site/); ensures site/.gitignore
	@$(VENV_BIN)/zensical build

# ============================================================================
# Lint Targets
# ============================================================================

##@ Lint

.PHONY: lint
lint: check-venv ## Run pre-commit (lint and format checks) on all files
	@$(VENV_BIN)/pre-commit run --all-files

# ============================================================================
# Cleanup Targets
# ============================================================================

##@ Cleanup

.PHONY: clean
clean: ## Remove temporary files, caches, and virtual environment
	@rm -rf $(CLEAN_RM) $(CLEAN_GLOB)
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
