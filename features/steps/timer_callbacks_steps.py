"""Step definitions for Timer on_start / on_end callbacks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, then

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- Given ---


@given("a {callback_kind} callback that records invocations")
@given("an {callback_kind} callback that records invocations")
def step_given_callback_records_invocations(
    context: Context,
    callback_kind: str,
) -> None:
    """Store list and callback that records each measurement."""
    invocations: list[timerun.Measurement] = []

    def record_invocation(m: timerun.Measurement) -> None:
        invocations.append(m)

    setattr(context, f"{callback_kind}_invocations", invocations)
    setattr(context, f"{callback_kind}_callback", record_invocation)


@given("a {callback_kind} callback that records timing state")
@given("an {callback_kind} callback that records timing state")
def step_given_callback_records_timing_state(
    context: Context,
    callback_kind: str,
) -> None:
    """Store callback that records timing snapshot."""

    def record_state(m: timerun.Measurement) -> None:
        setattr(context, f"{callback_kind}_wall_time", m.wall_time)
        setattr(context, f"{callback_kind}_cpu_time", m.cpu_time)

    setattr(context, f"{callback_kind}_callback", record_state)


# --- Then ---


@then("the {callback_kind} callback was called once")
def step_callback_called_once(context: Context, callback_kind: str) -> None:
    """Assert callback was invoked exactly once."""
    invocations = getattr(context, f"{callback_kind}_invocations")
    assert len(invocations) == 1, (
        f"expected {callback_kind} called once, got {len(invocations)}"
    )


@then("the {callback_kind} callback received the yielded measurement")
def step_callback_received_measurement(
    context: Context,
    callback_kind: str,
) -> None:
    """Assert callback received the yielded measurement instance."""
    invocations = getattr(context, f"{callback_kind}_invocations")
    assert invocations[0] is context.measurement


@then("both callbacks received the yielded measurement")
def step_both_callbacks_received_measurement(context: Context) -> None:
    """Assert both callbacks received the yielded measurement instance."""
    assert context.on_start_invocations[0] is context.measurement
    assert context.on_end_invocations[0] is context.measurement


@then("the measurement recorded by {callback_kind} had no timing spans")
def step_then_recorded_no_timing_spans(
    context: Context,
    callback_kind: str,
) -> None:
    """Assert timing spans were not yet populated during callback."""
    wall_time = getattr(context, f"{callback_kind}_wall_time")
    cpu_time = getattr(context, f"{callback_kind}_cpu_time")
    assert wall_time is None, f"Expected wall_time None, got {wall_time}"
    assert cpu_time is None, f"Expected cpu_time None, got {cpu_time}"


@then("the measurement recorded by {callback_kind} had valid timing spans")
def step_then_recorded_valid_timing_spans(
    context: Context,
    callback_kind: str,
) -> None:
    """Assert timing spans were populated during callback."""
    wall_time = getattr(context, f"{callback_kind}_wall_time")
    cpu_time = getattr(context, f"{callback_kind}_cpu_time")
    assert isinstance(wall_time, timerun.TimeSpan)
    assert isinstance(cpu_time, timerun.TimeSpan)
