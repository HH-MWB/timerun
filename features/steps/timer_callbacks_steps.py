"""Step definitions for Timer on_start / on_end callbacks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context


# --- Given ---


@given("an {callback_kind} callback that records invocations")
def step_given_callback_records_invocations(
    context: Context,
    callback_kind: str,
) -> None:
    """Store list and callback that records each measurement."""
    # List and callback that appends each measurement.
    invocations: list[timerun.Measurement] = []

    def record_invocation(m: timerun.Measurement) -> None:
        invocations.append(m)

    # Store on context for When/Then.
    setattr(context, f"{callback_kind}_invocations", invocations)
    setattr(context, f"{callback_kind}_callback", record_invocation)


# --- When ---


@when(
    "I measure a code block with a Timer that has that {callback_kind} "
    "callback",
)
def step_measure_block_with_callback(
    context: Context,
    callback_kind: str,
) -> None:
    """Measure with Timer callback; run trivial block."""
    callback = getattr(context, f"{callback_kind}_callback")
    with timerun.Timer(**{callback_kind: callback}) as context.measurement:
        pass


# --- Then ---


@then("the {callback_kind} callback was called once")
def step_callback_called_once(context: Context, callback_kind: str) -> None:
    """Assert callback was invoked exactly once."""
    invocations = getattr(context, f"{callback_kind}_invocations")
    assert len(invocations) == 1, (
        f"expected the {callback_kind} callback to be called once, "
        f"got {len(invocations)}"
    )


@then(
    "the {callback_kind} callback was called with the same measurement "
    "instance that the Timer yielded for that block",
)
def step_callback_called_with_the_measurement(
    context: Context,
    callback_kind: str,
) -> None:
    """Assert callback received the same measurement instance."""
    arg = getattr(context, f"{callback_kind}_invocations")[0]
    assert arg is context.measurement
