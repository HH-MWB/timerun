"""Step definitions for the Block timing feature."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from behave import given, then, when

import timerun
from features.steps.utils import (
    BUFFER_NS,
    assert_metadata_key_equals,
    assert_wall_time_within_buffer,
    sleep_wall_at_least,
    spin_wall_at_least,
)

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


@given("the {which} block duration is {duration_ns:n} nanoseconds")
def step_given_block_duration(
    context: Context,
    which: str,
    duration_ns: int,
) -> None:
    """Store block duration for which block."""
    setattr(context, f"{which}_block_ns", duration_ns)


@given('I will add metadata key "{key}" as "{value}" in the first block')
def step_given_metadata_add_in_first(
    context: Context,
    key: str,
    value: str,
) -> None:
    """First block will add key/value to metadata."""
    context.metadata_add_in_first = (key, value)


# --- When ---


@when("I measure the operation using `with`")
def step_measure_operation_using_with(context: Context) -> None:
    """Measure with Timer(); sleep or spin per operation_kind."""
    with timerun.Timer() as context.measurement:
        if getattr(context, "operation_kind", "blocking") == "CPU-bound":
            spin_wall_at_least(context.operation_duration_ns)
        else:
            sleep_wall_at_least(context.operation_duration_ns)


@when("I measure the async operation using `async with`")
def step_measure_async_using_async_with(context: Context) -> None:
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
            sleep_wall_at_least(context.thread_sleep_ns)
        return m

    # Run thread_count workers and collect measurements.
    with ThreadPoolExecutor(max_workers=thread_count) as ex:
        futures = [ex.submit(run) for _ in range(thread_count)]
        context.thread_measurements = [f.result() for f in futures]


@when("I measure two sequential blocks with the same Timer instance")
def step_measure_two_sequential_blocks(context: Context) -> None:
    """Measure two sequential blocks."""
    cm = timerun.Timer()

    with cm as context.first_measurement:
        sleep_wall_at_least(context.first_block_ns)

    with cm as context.second_measurement:
        sleep_wall_at_least(context.second_block_ns)


@when("I measure nested blocks with the same Timer instance")
def step_measure_nested_blocks(context: Context) -> None:
    """Measure nested blocks."""
    cm = timerun.Timer()

    with cm as context.outer_measurement:
        sleep_wall_at_least(context.outer_block_ns)

        with cm as context.inner_measurement:
            sleep_wall_at_least(context.inner_block_ns)


@when("I measure a code block with that metadata")
def step_measure_block_with_metadata(context: Context) -> None:
    """Measure with Timer(metadata=...); store result."""
    with timerun.Timer(metadata=context.metadata) as context.measurement:
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


# --- Then ---


@then("the measurement's CPU time is close to wall time")
def step_cpu_close_to_wall(context: Context) -> None:
    """Assert CPU close to wall time."""
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
    "the {which} measurement's wall time duration is within the configured "
    "buffer of {expected_ns:n} nanoseconds",
)
def step_which_measurement_wall_within_buffer(
    context: Context,
    which: str,
    expected_ns: int,
) -> None:
    """Assert which measurement wall time in buffer."""
    assert_wall_time_within_buffer(
        getattr(context, f"{which}_measurement"),
        expected_ns,
        BUFFER_NS,
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


@then('the {which} measurement\'s metadata key "{key}" is "{value}"')
def step_measurement_metadata_key(
    context: Context,
    which: str,
    key: str,
    value: str,
) -> None:
    """Assert which measurement metadata[key] is value."""
    assert_metadata_key_equals(
        getattr(context, f"{which}_measurement"),
        key,
        value,
    )


@then('the second measurement\'s metadata does not contain key "{key}"')
def step_second_measurement_metadata_no_key(
    context: Context,
    key: str,
) -> None:
    """Assert second measurement has no key."""
    assert key not in context.second_measurement.metadata


@then("the measurements are from different threads")
def step_measurements_from_different_threads(context: Context) -> None:
    """Assert N distinct measurements."""
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
