"""Step definitions shared by more than one feature.

Rule: a step belongs here only if its Gherkin text is used in multiple feature
files (e.g. block_timing.feature and function_timing.feature). Steps used by
a single feature live in that feature's step file (e.g. block_timing_steps.py).
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from behave import given, then

if TYPE_CHECKING:
    from behave.runner import Context

# Buffer: expected_ns <= duration <= expected_ns + BUFFER_NS (10 ms).
BUFFER_NS = 10_000_000

# --- Helpers ---


def _measurement(context: Context, which: str | None) -> object:
    """Resolve measurement from context."""
    if which is None:
        return context.measurement
    return getattr(context, f"{which}_measurement")


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
    # Required: an exception was stored by the When step.
    assert hasattr(context, "exception"), "Expected an exception to be raised"

    # Message must match.
    assert str(context.exception) == message


@then("an exception was propagated to the caller")
def step_exception_propagated(context: Context) -> None:
    """Assert ValueError was caught."""
    # Required: an exception was stored.
    assert hasattr(context, "exception")

    # Must be ValueError.
    assert isinstance(context.exception, ValueError)


@then(
    "the measurement's wall time duration is within the configured buffer of "
    "{expected_ns:n} nanoseconds",
)
@then(
    "the {which} measurement's wall time duration is within the configured "
    "buffer of {expected_ns:n} nanoseconds",
)
def step_wall_time_within_buffer(
    context: Context,
    expected_ns: int,
    which: str | None = None,
) -> None:
    """Assert wall time in buffer (default or first/second/outer/inner)."""
    measurement = _measurement(context, which)

    # Resolve duration and buffer bound.
    assert measurement.wall_time is not None
    duration = measurement.wall_time.duration
    max_ns = expected_ns + BUFFER_NS

    # Duration must lie in [expected_ns, expected_ns + buffer].
    assert expected_ns <= duration <= max_ns, (
        f"wall time {duration} not in [{expected_ns}, {max_ns}] "
        f"(buffer={BUFFER_NS})"
    )


@then(
    "the measurement's CPU time duration is within the configured buffer of "
    "{expected_ns:n} nanoseconds",
)
def step_cpu_time_within_buffer(context: Context, expected_ns: int) -> None:
    """Assert CPU time in buffer."""
    # Resolve duration and buffer bounds.
    assert context.measurement.cpu_time is not None

    # Duration must lie in [min_ns, max_ns].
    duration = context.measurement.cpu_time.duration
    min_ns = max(0, expected_ns - 1_000_000)
    max_ns = expected_ns + BUFFER_NS
    assert min_ns <= duration <= max_ns, (
        f"CPU time {duration} not in [{min_ns}, {max_ns}] (buffer={BUFFER_NS})"
    )


@then('the measurement\'s metadata key "{key}" is "{value}"')
@then('the {which} measurement\'s metadata key "{key}" is "{value}"')
def step_measurement_metadata_key_is(
    context: Context,
    key: str,
    value: str,
    which: str | None = None,
) -> None:
    """Assert metadata[key] is value (default or first/second/outer/inner)."""
    measurement = _measurement(context, which)
    assert measurement.metadata[key] == value
