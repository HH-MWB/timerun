"""Step definitions for Timer error handling."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context


class CustomAppError(Exception):
    """Custom domain exception for testing callback error propagation."""


# --- Given ---


@given("an on_start callback that raises an application exception")
def step_on_start_raises(context: Context) -> None:
    """Set up an on_start callback that raises CustomAppError."""

    def bad_callback(_m: timerun.Measurement) -> None:
        raise CustomAppError

    context.on_start_callback = bad_callback


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


@when("I call __exit__ on a Timer instance without calling __enter__ first")
def step_exit_without_enter(context: Context) -> None:
    """Call Timer().__exit__ without __enter__; store error."""
    try:
        timerun.Timer().__exit__(None, None, None)
    except RuntimeError as e:
        context.exception = e


@when("I use async with Timer from a callback on that loop")
def step_async_with_timer_no_current_task(context: Context) -> None:
    """Async with Timer from call_soon (no current task); store error."""
    loop = context.loop

    def callback() -> None:
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

    loop.call_soon(callback)
    loop.run_forever()
    loop.close()


@when("I call a decorated function that raises an exception")
def step_when_call_raising(context: Context) -> None:
    """Call raising function under Timer(); catch exception."""

    # Define raising function.
    @timerun.Timer()
    def raising() -> None:
        raise ValueError

    # Call and catch exception for Then to assert.
    try:
        raising()
    except ValueError as e:
        context.exception = e

    # Store function and measurement for Then.
    context.decorated_function = raising
    context.measurement = raising.measurements[-1]


@when("I call a decorated function with that on_start callback")
def step_call_decorated_function_with_on_start(context: Context) -> None:
    """Call a decorated function whose on_start raises; record exception."""

    @timerun.Timer(on_start=context.on_start_callback)
    def decorated_func() -> int:
        return 42

    try:
        decorated_func()
    except CustomAppError as exc:
        context.caught_exception = exc
        context.exception = exc


# --- Then ---


@then("the block yielded a measurement")
def step_block_yielded_measurement(context: Context) -> None:
    """Assert block produced a measurement."""
    assert context.measurement is not None
    assert context.measurement.wall_time is not None


@then("an exception was propagated to the caller")
def step_exception_propagated(context: Context) -> None:
    """Assert ValueError was caught."""
    # Required: an exception was stored.
    assert hasattr(context, "exception")

    # Must be ValueError.
    assert isinstance(context.exception, ValueError)


@then("the application exception is propagated to the caller")
def step_application_exception_propagated(context: Context) -> None:
    """Assert CustomAppError was propagated."""
    assert hasattr(context, "caught_exception"), "No exception was caught"
    assert isinstance(context.caught_exception, CustomAppError), (
        f"Expected CustomAppError, got "
        f"{type(context.caught_exception).__name__}"
    )


@then("no UnboundLocalError is raised")
def step_no_unbound_local_error(context: Context) -> None:
    """Assert no UnboundLocalError occurred."""
    assert not isinstance(context.caught_exception, UnboundLocalError)
