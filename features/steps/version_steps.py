"""Step definitions for the package version feature."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- Constants & Helpers ---

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+.*$")


# --- Given ---


@given("the timerun package is available")
def step_timerun_available(_: Context) -> None:
    """Ensure timerun module is available."""
    assert timerun is not None


# --- When ---


@when("I read the package version")
def step_read_version(context: Context) -> None:
    """Read and store package version."""
    context.version = getattr(timerun, "__version__", None)


# --- Then ---


@then("the version is a valid semantic version string")
def step_version_is_semver(context: Context) -> None:
    """Assert version is valid semantic version string."""
    assert isinstance(context.version, str), "Version is not a string"
    assert len(context.version) > 0, "Version string is empty"
    assert SEMVER_PATTERN.match(context.version), (
        f"Version {context.version!r} does not match semantic version format"
    )
