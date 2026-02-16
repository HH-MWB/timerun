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

# "duration within buffer of X": accept X <= duration <= X + BUFFER_NS.
# Covers sleep/scheduling jitter so tests don't flake.
BUFFER_NS = 10_000_000  # 10 ms
# CPU can be slightly below wall time (scheduling); allow 1 ms undershoot.
CPU_LOWER_SLACK_NS = 1_000_000


def sleep_wall_at_least(nanoseconds: int) -> None:
    """Sleep >= `nanoseconds` ns wall time. Jitter absorbed by BUFFER_NS."""
    time.sleep(nanoseconds / 1e9)


def spin_wall_at_least(nanoseconds: int) -> None:
    """Busy loop until wall time >= `nanoseconds` ns. Uses CPU."""
    start = time.perf_counter_ns()
    while time.perf_counter_ns() - start < nanoseconds:
        pass


# --- Given ---


@given("a blocking operation that takes around {duration_ns:n} nanoseconds")
def step_given_blocking_operation(context: Context, duration_ns: int) -> None:
    """Store duration for a blocking operation (e.g. time.sleep)."""
    context.operation_duration_ns = duration_ns


@given("an async operation that takes around {duration_ns:n} nanoseconds")
def step_given_async_operation(context: Context, duration_ns: int) -> None:
    """Store duration for an async operation (e.g. asyncio.sleep)."""
    context.operation_duration_ns = duration_ns


@given(
    "a CPU-bound operation that runs for around {duration_ns:n} nanoseconds",
)
def step_given_cpu_bound_operation(context: Context, duration_ns: int) -> None:
    """Store duration for a CPU-bound operation (busy-loop)."""
    context.operation_duration_ns = duration_ns


@given("each thread sleeps {duration_ns:n} nanoseconds")
def step_given_thread_sleep(context: Context, duration_ns: int) -> None:
    """Store duration for the two-thread scenario."""
    context.thread_sleep_ns = duration_ns


@given("the first block duration is {duration_ns:n} nanoseconds")
def step_given_first_block_duration(
    context: Context,
    duration_ns: int,
) -> None:
    """Store first block duration for sequential blocks."""
    context.first_block_ns = duration_ns


@given("the second block duration is {duration_ns:n} nanoseconds")
def step_given_second_block_duration(
    context: Context,
    duration_ns: int,
) -> None:
    """Store second block duration for sequential blocks."""
    context.second_block_ns = duration_ns


@given("the outer block duration is {duration_ns:n} nanoseconds")
def step_given_outer_block_duration(
    context: Context,
    duration_ns: int,
) -> None:
    """Store outer block duration for nested blocks."""
    context.outer_block_ns = duration_ns


@given("the inner block duration is {duration_ns:n} nanoseconds")
def step_given_inner_block_duration(
    context: Context,
    duration_ns: int,
) -> None:
    """Store inner block duration for nested blocks."""
    context.inner_block_ns = duration_ns


@given('metadata run_id "{run_id}" and tag "{tag}"')
def step_given_metadata(context: Context, run_id: str, tag: str) -> None:
    """Store metadata dict for use with BlockTimer(metadata=...)."""
    context.metadata = {"run_id": run_id, "tag": tag}


@given('I will add metadata key "{key}" as "{value}" in the first block')
def step_given_metadata_add_in_first(
    context: Context,
    key: str,
    value: str,
) -> None:
    """First block will add this key/value to measurement metadata."""
    context.metadata_add_in_first = (key, value)


# --- When ---


@when("I measure the blocking operation using `with`")
def step_measure_blocking_using_with(context: Context) -> None:
    """BlockTimer() around sleep_wall_at_least(operation_duration_ns)."""
    with timerun.BlockTimer() as context.measurement:
        sleep_wall_at_least(context.operation_duration_ns)


@when("I measure the async operation using `async with`")
def step_measure_async_using_async_with(context: Context) -> None:
    """Async BlockTimer() around asyncio.sleep(operation_duration_ns)."""

    # Define async task: BlockTimer around sleep.
    async def run() -> timerun.Measurement:
        async with timerun.BlockTimer() as m:
            await asyncio.sleep(context.operation_duration_ns / 1e9)
        return m

    # Run and store measurement.
    context.measurement = asyncio.run(run())


@when("I measure the CPU-bound operation using `with`")
def step_measure_cpu_bound_using_with(context: Context) -> None:
    """BlockTimer() around spin_wall_at_least(operation_duration_ns)."""
    with timerun.BlockTimer() as context.measurement:
        spin_wall_at_least(context.operation_duration_ns)


@when(
    "I measure blocks from {thread_count:n} threads "
    "using the same BlockTimer instance",
)
def step_measure_blocks_from_threads(
    context: Context,
    thread_count: int,
) -> None:
    """Measure blocks from thread_count threads (number from feature)."""
    # Store thread count for Then steps; one shared BlockTimer.
    context.thread_count = thread_count
    cm = timerun.BlockTimer()

    # Worker: enter timer, sleep, return measurement.
    def run() -> timerun.Measurement:
        with cm as m:
            sleep_wall_at_least(context.thread_sleep_ns)
        return m

    # Run thread_count workers and collect measurements.
    with ThreadPoolExecutor(max_workers=thread_count) as ex:
        futures = [ex.submit(run) for _ in range(thread_count)]
        context.thread_measurements = [f.result() for f in futures]


@when("I measure two sequential blocks with the same BlockTimer instance")
def step_measure_two_sequential_blocks(context: Context) -> None:
    """Measure two sequential blocks."""
    cm = timerun.BlockTimer()

    with cm as context.first_measurement:
        sleep_wall_at_least(context.first_block_ns)

    with cm as context.second_measurement:
        sleep_wall_at_least(context.second_block_ns)


@when("I measure nested blocks with the same BlockTimer instance")
def step_measure_nested_blocks(context: Context) -> None:
    """Measure nested blocks."""
    cm = timerun.BlockTimer()

    with cm as context.outer_measurement:
        sleep_wall_at_least(context.outer_block_ns)

        with cm as context.inner_measurement:
            sleep_wall_at_least(context.inner_block_ns)


@when("I measure a code block with that metadata")
def step_measure_block_with_metadata(context: Context) -> None:
    """BlockTimer(metadata=context.metadata), store the Measurement."""
    with timerun.BlockTimer(metadata=context.metadata) as context.measurement:
        pass


@when(
    "I measure two blocks with the same BlockTimer instance and that metadata",
)
def step_measure_two_blocks_with_metadata(context: Context) -> None:
    """Two blocks; Given may set metadata_add_in_first, mutate 1st."""
    cm = timerun.BlockTimer(metadata=context.metadata)
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
    """BlockTimer() around raising block; catch exception, keep measurement."""
    # Run timed block that raises; measurement still recorded on exit.
    try:
        with timerun.BlockTimer() as context.measurement:
            raise ValueError  # noqa: TRY301

    # Store exception for Then to assert.
    except ValueError as e:
        context.exception = e


@when(
    "I call __exit__ on a BlockTimer instance without calling __enter__ first",
)
def step_call_exit_without_enter(context: Context) -> None:
    """BlockTimer().__exit__ without __enter__; store exception in context."""
    try:
        timerun.BlockTimer().__exit__(None, None, None)
    except RuntimeError as e:
        context.exception = e


# --- Then ---


@then(
    "the measurement's wall time duration is between {min_ns:n} and "
    "{max_ns:n} nanoseconds",
)
def step_wall_time_between(context: Context, min_ns: int, max_ns: int) -> None:
    """Assert min_ns <= measurement.wall_time.duration <= max_ns."""
    # Required context validation.
    assert context.measurement.wall_time is not None

    # Duration in [min_ns, max_ns].
    duration = context.measurement.wall_time.duration
    assert min_ns <= duration <= max_ns, (
        f"wall time {duration} not in [{min_ns}, {max_ns}]"
    )


@then(
    "the measurement's wall time duration is within the configured buffer of "
    "{expected_ns:n} nanoseconds",
)
def step_wall_time_within_buffer(context: Context, expected_ns: int) -> None:
    """Assert expected_ns <= wall_time.duration <= expected_ns + buffer_ns."""
    # Required context validation.
    assert context.measurement.wall_time is not None

    # Duration in [expected_ns, expected_ns + BUFFER_NS].
    duration = context.measurement.wall_time.duration
    max_ns = expected_ns + BUFFER_NS
    assert expected_ns <= duration <= max_ns, (
        f"wall time {duration} not in [{expected_ns}, {max_ns}] "
        f"(buffer={BUFFER_NS})"
    )


@then(
    "the measurement's CPU time duration is within the configured buffer of "
    "{expected_ns:n} nanoseconds",
)
def step_cpu_time_within_buffer(context: Context, expected_ns: int) -> None:
    """cpu_time in [min_ns, expected_ns+buffer_ns]; allow undershoot."""
    # Required context validation.
    assert context.measurement.cpu_time is not None
    # Duration in [expected_ns - CPU_LOWER_SLACK_NS, expected_ns + BUFFER_NS].
    duration = context.measurement.cpu_time.duration
    min_ns = max(0, expected_ns - CPU_LOWER_SLACK_NS)
    max_ns = expected_ns + BUFFER_NS
    assert min_ns <= duration <= max_ns, (
        f"CPU time {duration} not in [{min_ns}, {max_ns}] (buffer={BUFFER_NS})"
    )


@then("the measurement's CPU time is close to wall time")
def step_cpu_close_to_wall(context: Context) -> None:
    """Assert wall - BUFFER_NS <= CPU <= wall (single-threaded)."""
    # Required context validation.
    assert context.measurement.wall_time is not None
    assert context.measurement.cpu_time is not None

    # Duration in [wall - BUFFER_NS, wall].
    wall = context.measurement.wall_time.duration
    cpu = context.measurement.cpu_time.duration
    min_cpu = max(0, wall - BUFFER_NS)
    assert min_cpu <= cpu <= wall, (
        f"CPU {cpu} not in [wall-BUFFER_NS, wall] = [{min_cpu}, {wall}]"
    )


@then(
    "each thread's measurement has wall time duration within the configured "
    "buffer of {expected_ns:n} nanoseconds",
)
def step_each_thread_wall_within_buffer(
    context: Context,
    expected_ns: int,
) -> None:
    """Each thread's wall_time in [expected_ns, expected_ns+buffer_ns]."""
    # Required context validation.
    measurements = context.thread_measurements
    assert len(measurements) == context.thread_count, (
        f"expected {context.thread_count} measurements, "
        f"got {len(measurements)}"
    )

    # Duration in [expected_ns, expected_ns + BUFFER_NS] per measurement.
    max_ns = expected_ns + BUFFER_NS
    for m in measurements:
        assert m.wall_time is not None
        assert expected_ns <= m.wall_time.duration <= max_ns, (
            f"wall time {m.wall_time.duration} not in "
            f"[{expected_ns}, {max_ns}] (buffer={BUFFER_NS})"
        )


@then("the measurements are from different threads")
def step_measurements_from_different_threads(context: Context) -> None:
    """Assert we have thread_count distinct measurements (one per thread)."""
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


@then(
    "the {which} measurement's wall time duration is within the configured "
    "buffer of {expected_ns:n} nanoseconds",
)
def step_which_measurement_wall_within_buffer(
    context: Context,
    which: str,
    expected_ns: int,
) -> None:
    """Outer/inner wall_time in [expected_ns, expected_ns+buffer_ns]."""
    # Required context validation.
    m = getattr(context, f"{which}_measurement")
    assert m.wall_time is not None

    # Duration in [expected_ns, expected_ns + BUFFER_NS].
    duration = m.wall_time.duration
    max_ns = expected_ns + BUFFER_NS
    assert expected_ns <= duration <= max_ns, (
        f"{which} wall time {duration} not in [{expected_ns}, {max_ns}] "
        f"(buffer={BUFFER_NS})"
    )


@then(
    "the outer measurement's wall time duration is at least the inner "
    "measurement's wall time duration",
)
def step_outer_wall_at_least_inner(context: Context) -> None:
    """Outer block duration >= inner (outer contains inner)."""
    # Required context validation: both have wall_time.
    assert context.outer_measurement.wall_time is not None
    assert context.inner_measurement.wall_time is not None

    # Duration: outer >= inner.
    outer_d = context.outer_measurement.wall_time.duration
    inner_d = context.inner_measurement.wall_time.duration
    assert outer_d >= inner_d, f"outer {outer_d} < inner {inner_d}"


@then('the first measurement\'s metadata key "{key}" is "{value}"')
def step_first_measurement_metadata_key(
    context: Context,
    key: str,
    value: str,
) -> None:
    """Assert the first measurement's metadata[key] equals value."""
    assert context.first_measurement.metadata[key] == value


@then('the second measurement\'s metadata key "{key}" is "{value}"')
def step_second_measurement_metadata_key(
    context: Context,
    key: str,
    value: str,
) -> None:
    """Assert the second measurement's metadata[key] equals value."""
    assert context.second_measurement.metadata[key] == value


@then('the second measurement\'s metadata does not contain key "{key}"')
def step_second_measurement_metadata_no_key(
    context: Context,
    key: str,
) -> None:
    """Second measurement's metadata lacks key (no leak from first block)."""
    assert key not in context.second_measurement.metadata


@then("an exception was propagated to the caller")
def step_exception_propagated(context: Context) -> None:
    """Assert we caught the exception that was raised inside the block."""
    assert hasattr(context, "exception")
    assert isinstance(context.exception, ValueError)
