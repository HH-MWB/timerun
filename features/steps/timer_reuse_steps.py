"""Step definitions for reusing one Timer across executions."""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context


# --- Given ---


@given("each thread sleeps {duration_ns:n} nanoseconds")
def step_given_thread_sleep(context: Context, duration_ns: int) -> None:
    """Store thread sleep duration."""
    context.thread_sleep_ns = duration_ns


@given("a Timer shared by both tasks")
def step_given_shared_timer(context: Context) -> None:
    """Create a Timer instance shared by task A and task B."""
    context.shared_timer = timerun.Timer()


@given("task {which} runs for {duration_ns:n} nanoseconds")
def step_given_task_duration(
    context: Context,
    which: str,
    duration_ns: int,
) -> None:
    """Define async function for the given task using the shared timer."""
    shared_timer = context.shared_timer
    duration_sec = duration_ns / 1e9

    async def run_task() -> timerun.Measurement:
        async with shared_timer as m:
            await asyncio.sleep(duration_sec)
        return m

    setattr(context, f"task_{which.lower()}_ns", duration_ns)
    setattr(context, f"task_{which.lower()}", run_task)


@given("task A starts before task B")
def step_given_task_a_starts_before_b(context: Context) -> None:
    """Store start order: A then B."""
    context.task_a_starts_before_b = True


@given("the {which} block duration is {duration_ns:n} nanoseconds")
def step_given_block_duration(
    context: Context,
    which: str,
    duration_ns: int,
) -> None:
    """Store block duration for the named block (first, second, etc.)."""
    setattr(context, f"{which}_block_ns", duration_ns)


# --- When ---


@when(
    "I measure blocks from {thread_count:n} threads "
    "using the same Timer instance",
)
def step_measure_blocks_from_threads(
    context: Context,
    thread_count: int,
) -> None:
    """Measure blocks from N threads."""
    context.thread_count = thread_count
    cm = timerun.Timer()

    # Worker: enter timer, sleep, return measurement.
    def run() -> timerun.Measurement:
        with cm as m:
            time.sleep(context.thread_sleep_ns / 1e9)
        return m

    # Run thread_count workers and collect measurements.
    with ThreadPoolExecutor(max_workers=thread_count) as ex:
        futures = [ex.submit(run) for _ in range(thread_count)]
        context.thread_measurements = [f.result() for f in futures]


@when("I measure two sequential blocks with the same Timer instance")
def step_measure_two_sequential_blocks(context: Context) -> None:
    """Measure two sequential blocks."""
    cm = timerun.Timer()

    # First block.
    with cm as context.first_measurement:
        time.sleep(context.first_block_ns / 1e9)

    # Second block.
    with cm as context.second_measurement:
        time.sleep(context.second_block_ns / 1e9)


@when("I measure nested blocks with the same Timer instance")
def step_measure_nested_blocks(context: Context) -> None:
    """Measure nested blocks."""
    cm = timerun.Timer()

    with cm as context.outer_measurement:
        time.sleep(context.outer_block_ns / 1e9)

        with cm as context.inner_measurement:
            time.sleep(context.inner_block_ns / 1e9)


@when("I run both tasks concurrently with the same Timer")
def step_run_both_tasks_concurrently(context: Context) -> None:
    """Run tasks concurrently, store results as first and second."""
    assert getattr(context, "task_a_starts_before_b", False), (
        "start order must be given (e.g. task A starts before task B)"
    )

    async def run_task_a_before_b() -> tuple[
        timerun.Measurement,
        timerun.Measurement,
    ]:
        return await asyncio.gather(context.task_a(), context.task_b())

    results = asyncio.run(run_task_a_before_b())
    context.first_measurement = results[0]
    context.second_measurement = results[1]


@when("I decorate it with Timer with maxlen {maxlen:n}")
def step_when_decorate_maxlen(context: Context, maxlen: int) -> None:
    """Store maxlen for next step."""
    context.func_maxlen = maxlen


@when("I call the decorated function {times:n} times")
def step_when_call_three_times(context: Context, times: int) -> None:
    """Decorate with Timer(maxlen=...), call N times."""

    @timerun.Timer(maxlen=context.func_maxlen)
    def sync_func() -> None:
        time.sleep(context.func_duration_ns / 1e9)

    # Call N times; only last maxlen measurements kept.
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
        time.sleep(context.func_duration_ns / 1e9)

    def run() -> None:
        sync_func()

    # Run thread_count workers concurrently.
    with ThreadPoolExecutor(max_workers=thread_count) as ex:
        futures = [ex.submit(run) for _ in range(thread_count)]
        for f in futures:
            f.result()

    # Store for Then.
    context.decorated_function = sync_func
    context.thread_count = thread_count


# --- Then ---


@then(
    "the outer measurement's wall time duration is at least the inner "
    "measurement's wall time duration",
)
def step_outer_wall_at_least_inner(context: Context) -> None:
    """Assert outer wall >= inner."""
    # Required context validation: both have wall_time.
    assert context.outer_measurement.wall_time is not None
    assert context.inner_measurement.wall_time is not None

    # Duration: outer >= inner.
    outer_d = context.outer_measurement.wall_time.duration
    inner_d = context.inner_measurement.wall_time.duration
    assert outer_d >= inner_d, f"outer {outer_d} < inner {inner_d}"


@then("the measurements are from different threads")
def step_measurements_from_different_threads(context: Context) -> None:
    """Assert thread_count distinct measurements."""
    # Required context validation.
    measurements = context.thread_measurements

    # Exactly thread_count measurements.
    assert len(measurements) == context.thread_count, (
        f"expected {context.thread_count} measurements, "
        f"got {len(measurements)}"
    )

    # All distinct (one measurement per thread).
    assert len(measurements) == len({id(m) for m in measurements}), (
        "measurements are not all distinct (one per thread)"
    )
