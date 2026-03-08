# TimeRun - Makefile
#
# Commands for development setup, testing, linting, and docs.
# Requires Python 3.10+ and pip.
#
# Usage: make [target] (run "make help" for all targets)

# ============================================================================
# Configuration (edit only the "Editable" block if needed)
# ============================================================================

# ---- Editable ----
# PYTHON: Interpreter for "make init". Empty = prompt; set to skip.
PYTHON ?=
# VENV_DIR: Virtualenv directory (e.g. .venv or venv).
VENV_DIR := .venv

# ---- Do Not Edit ----
COVERAGE_SOURCE := timerun
VENV_BIN := $(VENV_DIR)/bin
GITIGNORE_PATHS := \
	.gitignore \
	$(VENV_DIR) \
	.mypy_cache \
	.ruff_cache \
	.coverage \
	htmlcov \
	site
GITIGNORE_GLOBS := \
	*.pyc \
	*.egg-info \
	__pycache__

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
init: ## Set up dev env. Prompts for Python, or: make init PYTHON=python3.10
	@set -f; \
	printf '%s\n' $(GITIGNORE_PATHS) $(GITIGNORE_GLOBS) > .gitignore; \
	set +f;
	@if [ -n "$(PYTHON)" ]; then \
		py="$(PYTHON)"; \
	elif [ -t 0 ]; then \
		read -p "Which Python interpreter? [python3]: " py; \
		py=$${py:-python3}; \
	else \
		py=python3; \
	fi; \
	if [ ! -d "$(VENV_DIR)" ]; then $$py -m venv "$(VENV_DIR)" >/dev/null; fi
	@$(VENV_BIN)/pip install --upgrade pip >/dev/null
	@$(VENV_BIN)/pip install -e ".[dev,docs]" >/dev/null
	@$(VENV_BIN)/pip install pre-commit >/dev/null
	@$(VENV_BIN)/pre-commit install >/dev/null

.PHONY: clean
clean: ## Remove all files/dirs listed in .gitignore (inverse of init)
	@rm -rf $(GITIGNORE_PATHS)
	@set -f; \
	for p in $(GITIGNORE_GLOBS); do \
		find . -not -path './.git/*' -name "$$p" \
			-exec rm -rf {} + 2>/dev/null || true; \
	done; \
	set +f

# Internal: used by test, docs, lint; not shown in help
.PHONY: check-venv
check-venv:
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

.PHONY: test
test: BEHAVE_ARGS := -f null
test: test-verbose  ## Run BDD tests (summary + coverage; failures show which scenario failed)

.PHONY: test-verbose
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
