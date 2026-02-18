"""Step definitions for the time span feature."""

import operator
from datetime import timedelta

import parse
from behave import given, register_type, then, when
from behave.runner import Context

import timerun

# Gherkin relation phrases to operator functions for span comparison.
RELATION_OPERATORS = {
    "equals": operator.eq,
    "does not equal": operator.ne,
    "is less than": operator.lt,
    "is greater than": operator.gt,
    "is less than or equal to": operator.le,
    "is greater than or equal to": operator.ge,
}

register_type(
    Relation=parse.with_pattern(r"|".join(RELATION_OPERATORS))(
        lambda text: text.strip(),
    ),
)


# --- Given ---


@given("a time span from {start:n} to {end:n}")
def step_given_time_span(context: Context, start: int, end: int) -> None:
    """Create a TimeSpan(start, end) and store as context.time_span."""
    context.time_span = timerun.TimeSpan(start=start, end=end)


@given("span {name:w} of {duration:n} nanoseconds")
def step_given_span_of_duration(
    context: Context,
    name: str,
    duration: int,
) -> None:
    """Create a TimeSpan(0, duration) and store as context.time_span_<name>."""
    setattr(
        context,
        f"time_span_{name.lower()}",
        timerun.TimeSpan(start=0, end=duration),
    )


# --- When ---


@when("I try to create a time span from {start:n} to {end:n}")
def step_try_create_time_span(context: Context, start: int, end: int) -> None:
    """Create TimeSpan(start, end); store exception in context.exception."""
    try:
        timerun.TimeSpan(start=start, end=end)
    except Exception as e:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        context.exception = e


# --- Then ---


@then("the duration is {expected:n} nanoseconds")
def step_time_span_duration_is(context: Context, expected: int) -> None:
    """Assert context.time_span.duration equals expected."""
    assert context.time_span.duration == expected


@then("the timedelta is {seconds:f} seconds in standard Python timedelta type")
def step_timedelta_is_seconds_standard_type(
    context: Context,
    seconds: float,
) -> None:
    """Assert time_span.timedelta is timedelta and equals given seconds."""
    result = context.time_span.timedelta
    assert isinstance(result, timedelta)
    assert result == timedelta(seconds=seconds)


@then("time span A {relation:Relation} time span B")
def step_time_span_a_relation_b(context: Context, relation: str) -> None:
    """Assert time_span_a and time_span_b satisfy the given relation."""
    assert RELATION_OPERATORS[relation](
        context.time_span_a,
        context.time_span_b,
    )


@then("the {which:w} value is {expected:n}")
def step_time_span_value_is(
    context: Context,
    which: str,
    expected: int,
) -> None:
    """Assert time_span.start or time_span.end equals expected."""
    assert getattr(context.time_span, which) == expected
