"""Step definitions for the Block timing feature."""

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


@given('I will add metadata key "{key}" as "{value}" in the first block')
def step_given_metadata_add_in_first(
    context: Context,
    key: str,
    value: str,
) -> None:
    """First block will add key/value to metadata."""
    context.metadata_add_in_first = (key, value)


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


@given(
    "an event loop where code runs with no current asyncio task",
)
def step_given_event_loop_no_current_task(context: Context) -> None:
    """Store event loop with no current task (runs from When callback)."""
    context.loop = asyncio.new_event_loop()


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


@when("I measure a code block with that metadata")
def step_measure_block_with_metadata(context: Context) -> None:
    """Measure with Timer(metadata=...); store result."""
    with timerun.Timer(metadata=context.metadata) as context.measurement:
        pass


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


@when(
    "I measure two blocks with the same Timer instance and that metadata",
)
def step_measure_two_blocks_with_metadata(context: Context) -> None:
    """Measure two blocks; first may add metadata."""
    cm = timerun.Timer(metadata=context.metadata)

    # First block: optionally add key/value to measurement metadata.
    with cm as context.first_measurement:
        if hasattr(context, "metadata_add_in_first"):
            context.first_measurement.metadata[
                context.metadata_add_in_first[0]
            ] = context.metadata_add_in_first[1]

    # Second block: no extra metadata.
    with cm as context.second_measurement:
        pass


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


@then('the second measurement\'s metadata does not contain key "{key}"')
def step_second_measurement_metadata_no_key(
    context: Context,
    key: str,
) -> None:
    """Assert second measurement has no key."""
    assert key not in context.second_measurement.metadata


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


@then("the block yielded a measurement")
def step_block_yielded_measurement(context: Context) -> None:
    """Assert block produced a measurement."""
    assert context.measurement is not None
    assert context.measurement.wall_time is not None


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
