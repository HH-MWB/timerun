"""Step definitions for the Function timing feature."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun
from features.steps.utils import (
    sleep_wall_at_least,
)

if TYPE_CHECKING:
    from behave.runner import Context


# --- Given ---


@given("a sync function that sleeps for around {duration_ns:n} nanoseconds")
def step_given_sync_func_sleep(context: Context, duration_ns: int) -> None:
    """Store duration for a sync function that will sleep."""
    context.func_duration_ns = duration_ns


@given("an async function that sleeps for around {duration_ns:n} nanoseconds")
def step_given_async_func_sleep(context: Context, duration_ns: int) -> None:
    """Store duration for an async function that will sleep."""
    context.func_duration_ns = duration_ns


@given(
    "a sync generator that yields {count:n} items and sleeps "
    "{duration_ns:n} nanoseconds total",
)
def step_given_sync_gen(
    context: Context,
    count: int,
    duration_ns: int,
) -> None:
    """Store duration and yield count for sync gen (sleep across yields)."""
    context.gen_duration_ns = duration_ns
    context.gen_count = count


@given(
    "an async generator that yields {count:n} items and sleeps "
    "{duration_ns:n} nanoseconds total",
)
def step_given_async_gen(
    context: Context,
    count: int,
    duration_ns: int,
) -> None:
    """Store duration and yield count for an async generator."""
    context.gen_duration_ns = duration_ns
    context.gen_count = count


# --- When ---


@when("I call the decorated sync function")
def step_when_call_decorated_sync(context: Context) -> None:
    """Create sync function, decorate with FunctionTimer(), call it."""

    # Define decorated sync function (sleep for configured duration).
    @timerun.FunctionTimer()
    def sync_func() -> None:
        sleep_wall_at_least(context.func_duration_ns)

    # Call and store function + last measurement for Then steps.
    sync_func()
    context.decorated_function = sync_func
    context.measurement = sync_func.measurements[-1]


@when("I call the decorated async function")
def step_when_call_decorated_async(context: Context) -> None:
    """Create async function, decorate, run it."""

    # Define decorated async function (sleep for configured duration).
    @timerun.FunctionTimer()
    async def async_func() -> None:
        await asyncio.sleep(context.func_duration_ns / 1e9)

    # Run and store function + last measurement for Then steps.
    asyncio.run(async_func())
    context.decorated_function = async_func
    context.measurement = async_func.measurements[-1]


@when("I fully consume the decorated sync generator")
def step_when_consume_sync_gen(context: Context) -> None:
    """Create sync generator, decorate, consume fully."""
    per_sleep = context.gen_duration_ns // context.gen_count

    # Define decorated sync generator (sleep spread across yields).
    @timerun.FunctionTimer()
    def sync_gen() -> object:
        for i in range(context.gen_count):
            sleep_wall_at_least(per_sleep)
            yield i

    # Consume fully and store generator + last measurement for Then steps.
    list(sync_gen())
    context.decorated_function = sync_gen
    context.measurement = sync_gen.measurements[-1]


@when("I fully consume the decorated async generator")
def step_when_consume_async_gen(context: Context) -> None:
    """Create async generator, decorate, consume fully."""
    per_sleep = context.gen_duration_ns // context.gen_count

    # Define decorated async generator (sleep spread across yields).
    @timerun.FunctionTimer()
    async def async_gen() -> object:
        for i in range(context.gen_count):
            await asyncio.sleep(per_sleep / 1e9)
            yield i

    # Consume fully via event loop and store generator + last measurement.
    async def run() -> None:
        async for _ in async_gen():
            pass

    asyncio.run(run())
    context.decorated_function = async_gen
    context.measurement = async_gen.measurements[-1]


@when("I call a decorated function with that metadata")
def step_when_call_with_metadata(context: Context) -> None:
    """Decorate a no-op function with FunctionTimer(metadata=...), call it."""

    @timerun.FunctionTimer(metadata=context.metadata)
    def f() -> None:
        pass

    f()
    context.decorated_function = f
    context.measurement = f.measurements[-1]


@when("I call a decorated function that raises an exception")
def step_when_call_raising(context: Context) -> None:
    """Decorate a function that raises, call it, catch exception."""

    # Define decorated function that raises; measurement recorded on exit.
    @timerun.FunctionTimer()
    def raising() -> None:
        raise ValueError

    # Call, catch exception for Then to assert; store function and measurement.
    try:
        raising()
    except ValueError as e:
        context.exception = e
    context.decorated_function = raising
    context.measurement = raising.measurements[-1]


@when("I decorate it with FunctionTimer with maxlen {maxlen:n}")
def step_when_decorate_maxlen(context: Context, maxlen: int) -> None:
    """Store maxlen; actual decoration in next step."""
    context.func_maxlen = maxlen


@when("I call the decorated function {times:n} times")
def step_when_call_three_times(context: Context, times: int) -> None:
    """Decorate sync function with FunctionTimer(maxlen=...), call N times."""

    # Define decorated sync function with maxlen from previous step.
    @timerun.FunctionTimer(maxlen=context.func_maxlen)
    def sync_func() -> None:
        sleep_wall_at_least(context.func_duration_ns)

    # Call times times; only last maxlen measurements kept.
    for _ in range(times):
        sync_func()
    context.decorated_function = sync_func


@when(
    "I call the decorated function from {thread_count:n} threads concurrently",
)
def step_when_call_from_threads(context: Context, thread_count: int) -> None:
    """Create sync function, decorate, run it from thread_count threads."""

    # Define decorated sync function (sleep for configured duration).
    @timerun.FunctionTimer()
    def sync_func() -> None:
        sleep_wall_at_least(context.func_duration_ns)

    # Worker: call the timed function once.
    def run() -> None:
        sync_func()

    # Run thread_count workers concurrently; store function and count for Then.
    with ThreadPoolExecutor(max_workers=thread_count) as ex:
        futures = [ex.submit(run) for _ in range(thread_count)]
        for f in futures:
            f.result()
    context.decorated_function = sync_func
    context.thread_count = thread_count


# --- Then ---


@then("the decorated function's measurements deque has 1 entry")
def step_then_measurements_one(context: Context) -> None:
    """Assert len(decorated_function.measurements) == 1."""
    func = context.decorated_function
    assert hasattr(func, "measurements")
    assert len(func.measurements) == 1, (
        f"expected 1 measurement, got {len(func.measurements)}"
    )


@then("the decorated function's measurements deque has {n:n} entries")
def step_then_measurements_count(context: Context, n: int) -> None:
    """Assert len(decorated_function.measurements) == n."""
    func = context.decorated_function
    assert hasattr(func, "measurements")
    assert len(func.measurements) == n, (
        f"expected {n} measurements, got {len(func.measurements)}"
    )
