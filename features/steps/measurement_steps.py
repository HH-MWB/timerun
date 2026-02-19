"""Step definitions for the Measurement record feature."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- Given ---


@given("a {kind} time span from {start:n} to {end:n}")
def step_given_typed_time_span(
    context: Context,
    kind: str,
    start: int,
    end: int,
) -> None:
    """Set wall or CPU time span on context."""
    setattr(
        context,
        f"{kind.lower()}_time_span",
        timerun.TimeSpan(start=start, end=end),
    )


# --- When ---


@when("I create a measurement from the wall time span and the CPU time span")
def step_create_measurement_from_spans(context: Context) -> None:
    """Build Measurement from spans."""
    context.measurement = timerun.Measurement(
        wall_time=context.wall_time_span,
        cpu_time=context.cpu_time_span,
    )


@when('the metadata key "{key}" is set to "{value}"')
def step_measurement_metadata_key_set(
    context: Context,
    key: str,
    value: str,
) -> None:
    """Set measurement metadata[key]."""
    context.measurement.metadata[key] = value


# --- Then ---


@then("the measurement's {kind} time duration is {expected:n} nanoseconds")
def step_measurement_time_duration(
    context: Context,
    kind: str,
    expected: int,
) -> None:
    """Assert measurement duration equals expected."""
    assert (
        getattr(context.measurement, f"{kind.lower()}_time").duration
        == expected
    )


@then("the measurement's metadata is an empty dict")
def step_measurement_metadata_empty_dict(context: Context) -> None:
    """Assert metadata is empty dict."""
    metadata = context.measurement.metadata
    assert isinstance(metadata, dict)
    assert not metadata
