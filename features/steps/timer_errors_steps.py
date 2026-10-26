"""Step definitions for Timer error handling."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context


# --- Constants & Helpers ---


class CustomAppError(Exception):
    """Custom domain exception for testing callback error propagation."""


def _run_timer_coro_without_task(
    context: Context,
    loop: asyncio.AbstractEventLoop,
) -> None:
    """Run timer coroutine directly without an active Task."""

    async def use_timer() -> None:
        async with timerun.Timer():
            pass

    coro = use_timer()
    try:
        coro.send(None)
    except RuntimeError as e:
        context.exception = e
    except StopIteration:
        pass
    finally:
        coro.close()
    loop.stop()


# --- Given ---


@given("a Timer that has not been entered")
def step_given_timer_not_entered(context: Context) -> None:
    """Create un-entered timer."""
    context.timer = timerun.Timer()


@given("a {callback_kind} callback that raises an application exception")
@given("an {callback_kind} callback that raises an application exception")
def step_callback_raises(context: Context, callback_kind: str) -> None:
    """Set up a callback that raises CustomAppError."""

    def bad_callback(_m: timerun.Measurement) -> None:
        raise CustomAppError

    setattr(context, f"{callback_kind}_callback", bad_callback)


@given(
    "an event loop where code runs with no current asyncio task",
)
def step_given_event_loop_no_current_task(context: Context) -> None:
    """Store event loop with no current task (runs from When callback)."""
    context.loop = asyncio.new_event_loop()


# --- When ---


@when("I measure a code block that raises an exception")
def step_measure_block_raises(context: Context) -> None:
    """Measure raising block; catch exception."""
    try:
        with timerun.Timer() as context.measurement:
            raise ValueError  # noqa: TRY301
    except ValueError as e:
        context.exception = e


@when("I exit the timer")
def step_exit_without_enter(context: Context) -> None:
    """Call Timer().__exit__ without __enter__; store error."""
    timer = getattr(context, "timer", None) or timerun.Timer()
    try:
        timer.__exit__(None, None, None)
    except RuntimeError as e:
        context.exception = e


@when("I use async with Timer from a callback on that loop")
def step_async_with_timer_no_current_task(context: Context) -> None:
    """Async with Timer from call_soon (no current task); store error."""
    loop = context.loop
    loop.call_soon(lambda: _run_timer_coro_without_task(context, loop))
    loop.run_forever()
    loop.close()


@when("I call the decorated function that raises an exception")
def step_when_call_raising(context: Context) -> None:
    """Call raising function under Timer(); catch exception."""

    @timerun.Timer()
    def raising() -> None:
        raise ValueError

    try:
        raising()
    except ValueError as e:
        context.exception = e

    context.decorated_function = raising
    context.measurement = raising.measurements[-1]


# --- Then ---


@then("the block yielded a measurement")
def step_block_yielded_measurement(context: Context) -> None:
    """Assert block produced a measurement."""
    assert context.measurement is not None
    assert context.measurement.wall_time is not None
