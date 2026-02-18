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


@given(
    "a {kind} function that sleeps for around {duration_ns:n} nanoseconds",
)
@given(
    "an {kind} function that sleeps for around {duration_ns:n} nanoseconds",
)
def step_given_func_sleep(
    context: Context,
    kind: str,
    duration_ns: int,
) -> None:
    """Store func kind and duration."""
    context.func_duration_ns = duration_ns
    context.func_kind = kind


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


@when("I call the decorated function")
def step_when_call_decorated_func(context: Context) -> None:
    """Decorate function with Timer(), run it."""
    if context.func_kind == "async":

        @timerun.Timer()
        async def async_func() -> None:
            await asyncio.sleep(context.func_duration_ns / 1e9)

        asyncio.run(async_func())
        context.decorated_function = async_func
        context.measurement = async_func.measurements[-1]
    else:

        @timerun.Timer()
        def sync_func() -> None:
            sleep_wall_at_least(context.func_duration_ns)

        sync_func()
        context.decorated_function = sync_func
        context.measurement = sync_func.measurements[-1]


@when("I fully consume the decorated generator")
def step_when_consume_gen(context: Context) -> None:  # noqa: C901
    """Decorate generator with Timer(), consume fully."""
    per_sleep = context.gen_duration_ns // context.gen_count
    if context.gen_kind == "async":

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

        @timerun.Timer()
        def sync_gen() -> object:
            for i in range(context.gen_count):
                sleep_wall_at_least(per_sleep)
                yield i

        for _ in sync_gen():
            pass
        context.decorated_function = sync_gen
        context.measurement = sync_gen.measurements[-1]


@when("I call a decorated function with that metadata")
def step_when_call_with_metadata(context: Context) -> None:
    """Call no-op function decorated with Timer(metadata=...)."""

    @timerun.Timer(metadata=context.metadata)
    def f() -> None:
        pass

    f()
    context.decorated_function = f
    context.measurement = f.measurements[-1]


@when("I call a decorated function that raises an exception")
def step_when_call_raising(context: Context) -> None:
    """Call raising function under Timer(); catch exception."""

    @timerun.Timer()
    def raising() -> None:
        raise ValueError

    # Call, catch exception for Then to assert; store function and measurement.
    try:
        raising()
    except ValueError as e:
        context.exception = e
    context.decorated_function = raising
    context.measurement = raising.measurements[-1]


@when("I decorate it with Timer with maxlen {maxlen:n}")
def step_when_decorate_maxlen(context: Context, maxlen: int) -> None:
    """Store maxlen for next step."""
    context.func_maxlen = maxlen


@when("I call the decorated function {times:n} times")
def step_when_call_three_times(context: Context, times: int) -> None:
    """Decorate with Timer(maxlen=...), call N times."""

    @timerun.Timer(maxlen=context.func_maxlen)
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
    """Run decorated function from N threads."""

    @timerun.Timer()
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


@then("the decorated function's measurements deque has {n:n} entry")
@then("the decorated function's measurements deque has {n:n} entries")
def step_then_measurements_count(context: Context, n: int) -> None:
    """Assert measurements count is n."""
    func = context.decorated_function
    assert hasattr(func, "measurements")
    assert len(func.measurements) == n, (
        f"expected {n} measurements, got {len(func.measurements)}"
    )
