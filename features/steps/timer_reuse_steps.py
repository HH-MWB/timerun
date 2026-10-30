"""Step definitions for reusing one Timer across executions."""

from __future__ import annotations

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# --- Helpers ---


def _run_nested_sync(
    cm: timerun.Timer,
    outer_sec: float,
    inner_sec: float,
) -> tuple[timerun.Measurement, timerun.Measurement]:
    """Execute nested synchronous blocks."""
    with cm as m_out:
        time.sleep(outer_sec)
        with cm as m_in:
            time.sleep(inner_sec)
    return m_out, m_in


async def _run_nested_async(
    cm: timerun.Timer,
    modes: tuple[str, str],
    outer_sec: float,
    inner_sec: float,
) -> tuple[timerun.Measurement, timerun.Measurement]:
    """Execute nested blocks involving at least one async context."""
    outer_mode, inner_mode = modes

    async def run_inner() -> timerun.Measurement:
        if inner_mode == "async":
            async with cm as m_in:
                await asyncio.sleep(inner_sec)
            return m_in
        with cm as m_in:
            await asyncio.sleep(inner_sec)
        return m_in

    if outer_mode == "async":
        async with cm as m_out:
            await asyncio.sleep(outer_sec)
            m_in = await run_inner()
        return m_out, m_in

    with cm as m_out:
        await asyncio.sleep(outer_sec)
        m_in = await run_inner()
    return m_out, m_in


# --- Given ---


@given("the {which} block duration is {duration_ns:n} nanoseconds")
def step_given_block_duration(
    context: Context,
    which: str,
    duration_ns: int,
) -> None:
    """Store block duration for the named block (first, second, etc.)."""
    setattr(context, f"{which}_block_ns", duration_ns)


@given(
    "an async function that sleeps for {duration_ns:n} nanoseconds "
    "and calls the sync function",
)
def step_given_async_fn_calling_sync_fn(
    context: Context,
    duration_ns: int,
) -> None:
    """Define a decorated async function calling a decorated sync function."""
    timer = context.shared_timer
    sync_sleep_sec = getattr(context, "func_duration_ns", 0) / 1e9
    async_sleep_sec = duration_ns / 1e9
    return_val = 42

    @timer
    def sync_fn() -> int:
        if sync_sleep_sec:
            time.sleep(sync_sleep_sec)
        return return_val

    @timer
    async def async_fn() -> int:
        if async_sleep_sec:
            await asyncio.sleep(async_sleep_sec)
        return sync_fn()

    context.sync_function = sync_fn
    context.async_function = async_fn


@given("a shared Timer")
def step_given_shared_timer(context: Context) -> None:
    """Create a shared Timer instance."""
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


@given("child task {which:w} runs for {duration_ns:n} nanoseconds")
def step_given_child_task_duration(
    context: Context,
    which: str,
    duration_ns: int,
) -> None:
    """Store duration for child task."""
    setattr(context, f"child_task_{which}_duration_ns", duration_ns)


@given("each thread sleeps {duration_ns:n} nanoseconds")
def step_given_thread_sleep(context: Context, duration_ns: int) -> None:
    """Store thread sleep duration."""
    context.thread_sleep_ns = duration_ns


@given("a CPU-bound thread that runs for {duration_ns:n} nanoseconds")
def step_given_cpu_bound_thread(context: Context, duration_ns: int) -> None:
    """Store duration for CPU-bound thread."""
    context.cpu_thread_duration_ns = duration_ns


@given("an idle sleeping thread that runs for {duration_ns:n} nanoseconds")
def step_given_idle_sleeping_thread(
    context: Context,
    duration_ns: int,
) -> None:
    """Store duration for idle sleeping thread."""
    context.idle_thread_duration_ns = duration_ns


# --- When ---


@when(
    "I measure nested {outer_mode:w} and {inner_mode:w} blocks "
    "with the same Timer",
)
def step_when_measure_nested_blocks(
    context: Context,
    outer_mode: str,
    inner_mode: str,
) -> None:
    """Measure nested blocks for any combination of sync and async modes."""
    cm = timerun.Timer()
    outer_sec = context.outer_block_ns / 1e9
    inner_sec = context.inner_block_ns / 1e9

    if outer_mode == "sync" and inner_mode == "sync":
        res = _run_nested_sync(cm, outer_sec, inner_sec)
    else:
        res = asyncio.run(
            _run_nested_async(
                cm,
                (outer_mode, inner_mode),
                outer_sec,
                inner_sec,
            ),
        )

    context.outer_measurement, context.inner_measurement = res


@when("I call the decorated async function")
def step_when_call_decorated_async_function(context: Context) -> None:
    """Execute the decorated async function."""
    _ = asyncio.run(context.async_function())
    context.inner_measurement = context.sync_function.measurements[-1]
    context.outer_measurement = context.async_function.measurements[-1]


@when("I run both tasks concurrently with the same Timer")
def step_when_run_both_tasks_concurrently(context: Context) -> None:
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


@when(
    "I run both child tasks concurrently from within the active outer timer",
)
def step_when_run_child_tasks_within_active_timer(context: Context) -> None:
    """Execute concurrent child tasks from within an active timer block."""
    timer = context.shared_timer
    fast_ns = context.child_task_fast_duration_ns
    slow_ns = context.child_task_slow_duration_ns

    async def worker_fast() -> timerun.Measurement:
        async with timer as m:
            await asyncio.sleep(fast_ns / 1e9)
        return m

    async def worker_slow() -> timerun.Measurement:
        async with timer as m:
            await asyncio.sleep(slow_ns / 1e9)
        return m

    async def run() -> tuple[timerun.Measurement, timerun.Measurement]:
        async with timer:
            t1 = asyncio.create_task(worker_fast())
            await asyncio.sleep(0.001)
            t2 = asyncio.create_task(worker_slow())
            return await asyncio.gather(t1, t2)

    res_fast, res_slow = asyncio.run(run())
    context.child_task_fast_measurement = res_fast
    context.child_task_slow_measurement = res_slow


@when(
    "I measure blocks from {thread_count:n} threads "
    "using the same Timer instance",
)
def step_when_measure_blocks_from_threads(
    context: Context,
    thread_count: int,
) -> None:
    """Measure blocks from N threads."""
    context.thread_count = thread_count
    cm = timerun.Timer()

    def run() -> timerun.Measurement:
        with cm as m:
            time.sleep(context.thread_sleep_ns / 1e9)
        return m

    with ThreadPoolExecutor(max_workers=thread_count) as ex:
        futures = [ex.submit(run) for _ in range(thread_count)]
        context.thread_measurements = [f.result() for f in futures]


@when(
    "I call the decorated function from {thread_count:n} threads concurrently",
)
def step_when_call_from_threads(context: Context, thread_count: int) -> None:
    """Run decorated function from N threads."""

    @timerun.Timer()
    def sync_func() -> None:
        time.sleep(context.func_duration_ns / 1e9)

    with ThreadPoolExecutor(max_workers=thread_count) as ex:
        futures = [ex.submit(sync_func) for _ in range(thread_count)]
        for f in futures:
            f.result()

    context.decorated_function = sync_func
    context.thread_count = thread_count


@when("I measure both threads concurrently with the same Timer instance")
def step_when_measure_both_threads_concurrently(context: Context) -> None:
    """Run CPU-bound and idle threads concurrently with shared Timer."""
    timer = timerun.Timer()
    cpu_duration_sec = context.cpu_thread_duration_ns / 1e9
    idle_duration_sec = context.idle_thread_duration_ns / 1e9
    m_idle: timerun.Measurement | None = None

    def cpu_worker() -> None:
        with timer:
            start = time.process_time()
            while time.process_time() - start < cpu_duration_sec:
                pass

    def idle_worker() -> None:
        nonlocal m_idle
        with timer as m:
            time.sleep(idle_duration_sec)
        m_idle = m

    t1 = threading.Thread(target=cpu_worker)
    t2 = threading.Thread(target=idle_worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    context.idle_thread_measurement = m_idle


@when("I decorate the function with a Timer having maxlen {maxlen:n}")
def step_when_decorate_maxlen(context: Context, maxlen: int) -> None:
    """Store maxlen for next step."""
    context.func_maxlen = maxlen


@when("I call the decorated function {times:n} times")
def step_when_call_three_times(context: Context, times: int) -> None:
    """Decorate with Timer(maxlen=...), call N times."""

    @timerun.Timer(maxlen=context.func_maxlen)
    def sync_func() -> None:
        time.sleep(context.func_duration_ns / 1e9)

    for _ in range(times):
        sync_func()

    context.decorated_function = sync_func


# --- Then ---


@then(
    "the outer measurement's wall time duration "
    "is at least the inner measurement's wall time duration",
)
def step_then_outer_wall_at_least_inner(context: Context) -> None:
    """Assert outer wall >= inner."""
    assert context.outer_measurement.wall_time is not None
    assert context.inner_measurement.wall_time is not None

    outer_d = context.outer_measurement.wall_time.duration
    inner_d = context.inner_measurement.wall_time.duration
    assert outer_d >= inner_d, f"outer {outer_d} < inner {inner_d}"


@then("each decorated function has recorded {n:n} measurement")
@then("each decorated function has recorded {n:n} measurements")
def step_then_each_decorated_function_recorded(
    context: Context,
    n: int,
) -> None:
    """Assert each decorated function recorded N measurements."""
    assert len(context.sync_function.measurements) == n, (
        f"expected {n} measurements, got "
        f"{len(context.sync_function.measurements)}"
    )
    assert len(context.async_function.measurements) == n, (
        f"expected {n} measurements, got "
        f"{len(context.async_function.measurements)}"
    )


@then("the measurements are from different threads")
def step_then_measurements_from_different_threads(context: Context) -> None:
    """Assert thread_count distinct measurements."""
    measurements = context.thread_measurements

    assert len(measurements) == context.thread_count, (
        f"expected {context.thread_count} measurements, "
        f"got {len(measurements)}"
    )

    assert len(measurements) == len({id(m) for m in measurements}), (
        "measurements are not all distinct (one per thread)"
    )
