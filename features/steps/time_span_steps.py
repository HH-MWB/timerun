"""Step definitions for the time span feature."""

from __future__ import annotations

import operator
from datetime import timedelta
from typing import TYPE_CHECKING

import parse
from behave import given, register_type, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

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
    """Create TimeSpan, store on context."""
    context.time_span = timerun.TimeSpan(start=start, end=end)


@given("span {name:w} of {duration:n} nanoseconds")
def step_given_span_of_duration(
    context: Context,
    name: str,
    duration: int,
) -> None:
    """Create TimeSpan(0, duration), store as named."""
    setattr(
        context,
        f"time_span_{name.lower()}",
        timerun.TimeSpan(start=0, end=duration),
    )


# --- When ---


@when("I try to create a time span from {start:n} to {end:n}")
def step_try_create_time_span(context: Context, start: int, end: int) -> None:
    """Create TimeSpan; store exception."""
    try:
        timerun.TimeSpan(start=start, end=end)
    except Exception as e:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        context.exception = e


# --- Then ---


@then("the duration is {expected:n} nanoseconds")
def step_time_span_duration_is(context: Context, expected: int) -> None:
    """Assert time_span duration."""
    assert context.time_span.duration == expected


@then("the timedelta is {seconds:f} seconds in standard Python timedelta type")
def step_timedelta_is_seconds_standard_type(
    context: Context,
    seconds: float,
) -> None:
    """Assert timedelta equals seconds."""
    result = context.time_span.timedelta
    assert isinstance(result, timedelta)
    assert result == timedelta(seconds=seconds)


@then("time span A {relation:Relation} time span B")
def step_time_span_a_relation_b(context: Context, relation: str) -> None:
    """Assert two time spans satisfy relation."""
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
    """Assert start or end equals expected."""
    assert getattr(context.time_span, which) == expected
