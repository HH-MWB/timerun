"""Step definitions for the package version feature."""

from behave import then, when
from behave.runner import Context

import timerun

# --- When ---


@when("I read the package version")
def step_read_version(context: Context) -> None:
    """Read the package version and store it for Then steps."""
    context.version = getattr(timerun, "__version__", None)


# --- Then ---


@then("the package has a version")
def step_package_has_version(context: Context) -> None:
    """Assert the package exposes a version."""
    assert context.version is not None


@then("the version is a non-empty string")
def step_version_non_empty_string(context: Context) -> None:
    """Assert the version is a non-empty string."""
    assert isinstance(context.version, str)
    assert len(context.version) > 0
