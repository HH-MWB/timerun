"""Shared step definitions used by multiple features.

Steps here use consistent wording and semantics across features
(exception assertions, error messages, measurement metadata, wall time buffer).
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from behave import given, then

from features.steps.utils import (
    BUFFER_NS,
    CPU_LOWER_SLACK_NS,
    assert_metadata_key_equals,
    assert_wall_time_within_buffer,
)

if TYPE_CHECKING:
    from behave.runner import Context


# --- Given ---


@given('metadata run_id "{run_id}" and tag "{tag}"')
def step_given_metadata(context: Context, run_id: str, tag: str) -> None:
    """Store metadata for Timer."""
    context.metadata = {"run_id": run_id, "tag": tag}


# --- Then ---


@then("a {exception_type} is raised")
def step_exception_raised(context: Context, exception_type: str) -> None:
    """Assert stored exception type."""
    # Required: an exception was stored by the When step.
    assert hasattr(context, "exception"), "Expected an exception to be raised"

    # Type must match (e.g. ValueError, RuntimeError).
    assert isinstance(context.exception, getattr(builtins, exception_type)), (
        f"Expected {exception_type}, got {type(context.exception).__name__}"
    )


@then('the error message is "{message}"')
def step_error_message_is(context: Context, message: str) -> None:
    """Assert exception message."""
    assert hasattr(context, "exception"), "Expected an exception to be raised"
    assert str(context.exception) == message


@then("an exception was propagated to the caller")
def step_exception_propagated(context: Context) -> None:
    """Assert ValueError was caught."""
    assert hasattr(context, "exception")
    assert isinstance(context.exception, ValueError)


@then(
    "the measurement's wall time duration is within the configured buffer of "
    "{expected_ns:n} nanoseconds",
)
def step_wall_time_within_buffer(context: Context, expected_ns: int) -> None:
    """Assert wall time in buffer."""
    assert_wall_time_within_buffer(context.measurement, expected_ns, BUFFER_NS)


@then(
    "the measurement's CPU time duration is within the configured buffer of "
    "{expected_ns:n} nanoseconds",
)
def step_cpu_time_within_buffer(context: Context, expected_ns: int) -> None:
    """Assert CPU time in buffer."""
    assert context.measurement.cpu_time is not None
    duration = context.measurement.cpu_time.duration
    min_ns = max(0, expected_ns - CPU_LOWER_SLACK_NS)
    max_ns = expected_ns + BUFFER_NS
    assert min_ns <= duration <= max_ns, (
        f"CPU time {duration} not in [{min_ns}, {max_ns}] (buffer={BUFFER_NS})"
    )


@then('the measurement\'s metadata key "{key}" is "{value}"')
def step_measurement_metadata_key_is(
    context: Context,
    key: str,
    value: str,
) -> None:
    """Assert metadata[key] is value."""
    assert_metadata_key_equals(context.measurement, key, value)
