"""Step definitions for the time span feature."""

from __future__ import annotations

import operator
from dataclasses import FrozenInstanceError
from datetime import timedelta
from typing import TYPE_CHECKING

import parse
from behave import given, register_type, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- Constants & Helpers ---

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

UNSUPPORTED_OPERANDS: dict[str, object] = {
    "an integer": 1_000_000,
    "a float": 1.5,
    "a string": "1,000,000",
    "another time span": timerun.TimeSpan(start=0, end=2_000_000),
}


# --- Given ---


@given("a time span from {start:n} to {end:n}")
@given("a time span {name:w} from {start:n} to {end:n}")
def step_given_time_span(
    context: Context,
    start: int,
    end: int,
    name: str | None = None,
) -> None:
    """Create TimeSpan, store on context (as time_span or named)."""
    attr = "time_span" if name is None else f"time_span_{name.lower()}"
    setattr(context, attr, timerun.TimeSpan(start=start, end=end))


@given("span {name:w} with duration {duration:n} nanoseconds")
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


@when("I read the duration")
def step_when_read_duration(context: Context) -> None:
    """Read the duration property."""
    context.read_duration = context.time_span.duration


@when("I read the start and end values")
def step_when_read_start_end(context: Context) -> None:
    """Read start and end values."""
    context.read_start = context.time_span.start
    context.read_end = context.time_span.end


@when("I read the duration as a timedelta")
def step_when_read_timedelta(context: Context) -> None:
    """Read duration as timedelta."""
    context.read_timedelta = context.time_span.timedelta


@when("I compare time span A and time span B")
def step_when_compare_spans(context: Context) -> None:
    """Compare two spans for equality."""
    context.spans_equal = context.time_span_a == context.time_span_b


@when("I compare the durations of span A and span B")
def step_when_compare_durations(_: Context) -> None:
    """Compare durations of two spans."""


@when("I try to create a time span from {start:n} to {end:n}")
def step_try_create_time_span(context: Context, start: int, end: int) -> None:
    """Create TimeSpan; store exception."""
    try:
        timerun.TimeSpan(start=start, end=end)
    except ValueError as e:
        context.exception = e


@when("I try to modify the start value")
def step_when_modify_start_value(context: Context) -> None:
    """Attempt modifying frozen start attribute; store exception."""
    try:
        context.time_span.start = 999
    except FrozenInstanceError as exc:
        context.exception = exc


@when("I compare whether the time span is less than {operand}")
def step_compare_time_span_less_than(
    context: Context,
    operand: str,
) -> None:
    """Attempt ordering comparison between TimeSpan and specified operand."""
    target = UNSUPPORTED_OPERANDS[operand]
    try:
        _ = context.time_span < target
    except TypeError as e:
        context.exception = e


# --- Then ---


@then("the duration is {expected:n} nanoseconds")
def step_time_span_duration_is(context: Context, expected: int) -> None:
    """Assert time_span duration."""
    assert context.time_span.duration == expected


@then("the timedelta is {seconds:f} seconds")
def step_timedelta_is_seconds_standard_type(
    context: Context,
    seconds: float,
) -> None:
    """Assert timedelta equals seconds."""
    result = context.time_span.timedelta
    assert isinstance(result, timedelta)
    assert result == timedelta(seconds=seconds)


@then("time span A's duration {relation:Relation} time span B's duration")
def step_time_span_a_duration_relation_b(
    context: Context,
    relation: str,
) -> None:
    """Assert two time span durations satisfy relation."""
    assert RELATION_OPERATORS[relation](
        context.time_span_a.duration,
        context.time_span_b.duration,
    )


@then("time span A does not equal time span B")
def step_time_span_a_not_equal_b(context: Context) -> None:
    """Assert time span A does not equal time span B."""
    assert context.time_span_a != context.time_span_b


@then("the {which:w} value is {expected:n}")
def step_time_span_value_is(
    context: Context,
    which: str,
    expected: int,
) -> None:
    """Assert start or end equals expected."""
    assert getattr(context.time_span, which) == expected


@then("both spans are distinct when collected in a set")
def step_spans_in_set_produces(context: Context, count: int = 2) -> None:
    """Assert putting span A and span B in a set produces count elements."""
    span_set = {context.time_span_a, context.time_span_b}
    assert len(span_set) == count, (
        f"Expected {count} elements in set, got {len(span_set)}"
    )
