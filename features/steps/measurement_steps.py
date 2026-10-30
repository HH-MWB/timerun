"""Step definitions for the Measurement record feature."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- Given ---


@given("a default measurement")
def step_create_default_measurement(context: Context) -> None:
    """Create a default Measurement instance."""
    context.measurement = timerun.Measurement()


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


@when("I set the measurement metadata:")
def step_set_measurement_metadata_table(context: Context) -> None:
    """Set measurement metadata from table."""
    for row in context.table:
        context.measurement.metadata[row["key"]] = row["value"]


# --- Then ---


@then("the measurement's metadata is empty")
def step_measurement_metadata_empty(context: Context) -> None:
    """Assert metadata is empty."""
    assert context.measurement.metadata == {}
