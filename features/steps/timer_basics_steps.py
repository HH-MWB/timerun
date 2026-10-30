"""Step definitions for basic timing (operations, generators, return types)."""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- Helpers ---


def _consume_async_gen(
    count: int,
    per_sleep: int,
) -> tuple[object, timerun.Measurement]:
    """Create and fully consume a timed async generator."""

    @timerun.Timer()
    async def async_gen() -> object:
        for i in range(count):
            await asyncio.sleep(per_sleep / 1e9)
            yield i

    async def run() -> None:
        async for _ in async_gen():
            pass

    asyncio.run(run())
    return async_gen, async_gen.measurements[-1]


def _consume_sync_gen(
    count: int,
    per_sleep: int,
    limit: int | None = None,
) -> tuple[object, timerun.Measurement]:
    """Create and consume a timed sync generator up to limit (or all)."""

    @timerun.Timer()
    def sync_gen() -> object:
        for i in range(count):
            time.sleep(per_sleep / 1e9)
            yield i

    for idx, _ in enumerate(sync_gen(), start=1):
        if limit is not None and idx == limit:
            break

    return sync_gen, sync_gen.measurements[-1]


# --- Given ---


@given("a {kind} operation that runs for {duration_ns:n} nanoseconds")
@given("an {kind} operation that runs for {duration_ns:n} nanoseconds")
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


@given("a function with a typed return signature")
def step_given_typed_function(context: Context) -> None:
    """Define a function with an explicit return type."""

    def compute_answer() -> int:
        return 42

    context.original_func = compute_answer


# --- When ---


@when("I measure the operation")
def step_measure_operation(context: Context) -> None:
    """Measure with Timer(); sleep or spin per operation_kind."""
    if context.operation_kind == "async":

        async def run() -> timerun.Measurement:
            async with timerun.Timer() as m:
                await asyncio.sleep(context.operation_duration_ns / 1e9)
            return m

        context.measurement = asyncio.run(run())
    elif context.operation_kind == "CPU-bound":
        with timerun.Timer() as context.measurement:
            start = time.process_time_ns()
            while (
                time.process_time_ns() - start < context.operation_duration_ns
            ):
                pass
    else:
        with timerun.Timer() as context.measurement:
            time.sleep(context.operation_duration_ns / 1e9)


@when("I fully consume the decorated generator")
@when("I consume only {count:n} items from the decorated generator")
def step_when_consume_gen(context: Context, count: int | None = None) -> None:
    """Decorate generator with Timer(), consume fully or up to count."""
    per_sleep = context.gen_duration_ns // context.gen_count
    if context.gen_kind == "async":
        func, measurement = _consume_async_gen(context.gen_count, per_sleep)
    else:
        func, measurement = _consume_sync_gen(
            context.gen_count,
            per_sleep,
            limit=count,
        )

    context.decorated_function = func
    context.measurement = measurement


@when("I decorate the function with Timer")
def step_decorate_function_with_timer(context: Context) -> None:
    """Decorate the function with Timer()."""
    context.decorated_func = timerun.Timer()(context.original_func)


# --- Then ---


@then("the decorated function preserves the original return type")
def step_assert_return_type_preserved(context: Context) -> None:
    """Assert decorated function preserves return type and signature."""
    orig_type = inspect.signature(context.original_func).return_annotation
    dec_type = inspect.signature(context.decorated_func).return_annotation
    assert orig_type == dec_type, (
        f"Expected return type {orig_type}, got {dec_type}"
    )

    # Verify decorator call signature does not widen to a generator union
    sig = inspect.signature(timerun.Timer.__call__)
    ret_str = str(sig.return_annotation)
    assert not ("AsyncGenerator" in ret_str and "Generator" in ret_str), (
        f"Timer.__call__ return annotation is a broad union: {ret_str}"
    )
