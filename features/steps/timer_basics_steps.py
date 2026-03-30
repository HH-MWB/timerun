"""Step definitions for basic timing (blocks, functions, generators)."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun
from features.steps.common_steps import BUFFER_NS

if TYPE_CHECKING:
    from behave.runner import Context


# --- Given ---


@given(
    "a {kind} operation that runs for around {duration_ns:n} nanoseconds",
)
@given(
    "an {kind} operation that runs for around {duration_ns:n} nanoseconds",
)
def step_given_operation(
    context: Context,
    kind: str,
    duration_ns: int,
) -> None:
    """Store operation duration and kind."""
    context.operation_duration_ns = duration_ns
    context.operation_kind = kind


@given(
    "a {kind} generator that yields {count:n} items and sleeps "
    "{duration_ns:n} nanoseconds total",
)
@given(
    "an {kind} generator that yields {count:n} items and sleeps "
    "{duration_ns:n} nanoseconds total",
)
def step_given_gen(
    context: Context,
    kind: str,
    count: int,
    duration_ns: int,
) -> None:
    """Store generator kind, duration and count."""
    context.gen_duration_ns = duration_ns
    context.gen_count = count
    context.gen_kind = kind


# --- When ---


@when("I measure the operation using `with`")
def step_measure_sync_operation_using_with(context: Context) -> None:
    """Measure with Timer(); sleep or spin per operation_kind."""
    with timerun.Timer() as context.measurement:
        if context.operation_kind == "CPU-bound":
            # Spin until duration elapsed.
            start = time.process_time_ns()
            while (
                time.process_time_ns() - start < context.operation_duration_ns
            ):
                pass
        else:
            # Sleep for duration.
            time.sleep(context.operation_duration_ns / 1e9)


@when("I measure the async operation using `async with`")
def step_measure_async_operation_using_async_with(context: Context) -> None:
    """Measure async with Timer(); asyncio.sleep."""

    async def run() -> timerun.Measurement:
        async with timerun.Timer() as m:
            await asyncio.sleep(context.operation_duration_ns / 1e9)
        return m

    context.measurement = asyncio.run(run())


@when("I call the decorated function")
def step_when_call_decorated_func(context: Context) -> None:
    """Decorate function with Timer(), run it."""
    if context.func_kind == "async":
        # Define async function, run it, store function and measurement.
        @timerun.Timer()
        async def async_func() -> None:
            await asyncio.sleep(context.func_duration_ns / 1e9)

        asyncio.run(async_func())
        context.decorated_function = async_func
        context.measurement = async_func.measurements[-1]
    else:
        # Define sync function, run it, store function and measurement.
        @timerun.Timer()
        def sync_func() -> None:
            time.sleep(context.func_duration_ns / 1e9)

        sync_func()
        context.decorated_function = sync_func
        context.measurement = sync_func.measurements[-1]


@when("I fully consume the decorated generator")
def step_when_consume_gen(context: Context) -> None:  # noqa: C901
    """Decorate generator with Timer(), consume fully."""
    per_sleep = context.gen_duration_ns // context.gen_count

    if context.gen_kind == "async":
        # Define async gen and runner; consume; store func and measurement.
        @timerun.Timer()
        async def async_gen() -> object:
            for i in range(context.gen_count):
                await asyncio.sleep(per_sleep / 1e9)
                yield i

        async def run() -> None:
            async for _ in async_gen():
                pass

        asyncio.run(run())
        context.decorated_function = async_gen
        context.measurement = async_gen.measurements[-1]
    else:
        # Define sync generator; consume; store function and measurement.
        @timerun.Timer()
        def sync_gen() -> object:
            for i in range(context.gen_count):
                time.sleep(per_sleep / 1e9)
                yield i

        for _ in sync_gen():
            pass
        context.decorated_function = sync_gen
        context.measurement = sync_gen.measurements[-1]


# --- Then ---


@then(
    "the measurement's wall time duration is at least {expected_ns:n} "
    "nanoseconds",
)
def step_measurement_wall_time_at_least(
    context: Context,
    expected_ns: int,
) -> None:
    """Assert wall time >= expected."""
    # Require wall_time and get duration.
    assert context.measurement.wall_time is not None
    duration = context.measurement.wall_time.duration

    # Duration must be at least expected.
    assert duration >= expected_ns, (
        f"wall time {duration} < expected {expected_ns}"
    )


@then(
    "the measurement's CPU time duration is within the configured buffer of "
    "{expected_ns:n} nanoseconds",
)
def step_cpu_time_within_buffer(context: Context, expected_ns: int) -> None:
    """Assert CPU time in buffer."""
    # Resolve duration and buffer bounds.
    assert context.measurement.cpu_time is not None

    # Duration must lie in [min_ns, max_ns].
    duration = context.measurement.cpu_time.duration
    min_ns = max(0, expected_ns - 1_000_000)
    max_ns = expected_ns + BUFFER_NS
    assert min_ns <= duration <= max_ns, (
        f"CPU time {duration} not in [{min_ns}, {max_ns}] (buffer={BUFFER_NS})"
    )
