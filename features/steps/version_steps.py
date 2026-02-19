"""Step definitions for the package version feature."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- When ---


@when("I read the package version")
def step_read_version(context: Context) -> None:
    """Read and store package version."""
    context.version = getattr(timerun, "__version__", None)


# --- Then ---


@then("the version is a non-empty string")
def step_version_non_empty_string(context: Context) -> None:
    """Assert version is non-empty string."""
    assert isinstance(context.version, str)
    assert len(context.version) > 0
