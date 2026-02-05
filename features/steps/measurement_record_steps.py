"""Step definitions for the Measurement record feature."""

from behave import given, then, when
from behave.runner import Context

import timerun

# --- Given ---


@given("a {kind} time span from {start:n} to {end:n}")
def step_given_typed_time_span(
    context: Context,
    kind: str,
    start: int,
    end: int,
) -> None:
    """Set time span to context based on kind (wall/CPU)."""
    span = timerun.TimeSpan(start=start, end=end)
    setattr(context, f"{kind.lower()}_time_span", span)


# --- When ---


@when("I create a measurement from the wall time span and the CPU time span")
def step_create_measurement_from_spans(context: Context) -> None:
    """Build Measurement from wall/cpu spans; set context.measurement."""
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
    """Set the measurement's metadata[key] to value."""
    context.measurement.metadata[key] = value


# --- Then ---


@then("the measurement's {kind} time duration is {expected:n} nanoseconds")
def step_measurement_time_duration(
    context: Context,
    kind: str,
    expected: int,
) -> None:
    """Assert measurement wall_time or cpu_time duration equals expected."""
    assert (
        getattr(context.measurement, f"{kind.lower()}_time").duration
        == expected
    )


@then("the measurement's metadata is an empty dict")
def step_measurement_metadata_empty_dict(context: Context) -> None:
    """Assert the measurement's metadata is a dict and empty."""
    metadata = context.measurement.metadata
    assert isinstance(metadata, dict)
    assert not metadata


@then('the measurement\'s metadata key "{key}" is "{value}"')
def step_measurement_metadata_key_value(
    context: Context,
    key: str,
    value: str,
) -> None:
    """Assert the measurement's metadata[key] equals value."""
    assert context.measurement.metadata[key] == value
