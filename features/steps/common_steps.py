"""Step definitions shared by more than one feature.

Rule: a step belongs here only if its Gherkin text is used in multiple feature
files (e.g. timer_basics.feature and timer_metadata.feature). Steps used by
a single feature live in that feature's step file (e.g. timer_basics_steps.py).
"""

from __future__ import annotations

import asyncio
import builtins
import time
from typing import TYPE_CHECKING, Any

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context

# Tolerance buffers:
# Wall time: expected_ns <= duration <= expected_ns + BUFFER_NS (5 ms).
BUFFER_NS = 5_000_000
# CPU time lower-bound tolerance: max(0, expected_ns - CPU_TOLERANCE_NS).
CPU_TOLERANCE_NS = 500_000  # 0.5 ms


# --- Helpers ---


def _measurement(context: Context, which: str | None) -> timerun.Measurement:
    """Resolve measurement from context by target name."""
    if which is None:
        return context.measurement

    cleaned = which.strip().lower().replace("-", "_").replace(" ", "_")
    cleaned = cleaned.removeprefix("the_")
    cleaned = cleaned.removesuffix("_measurement")
    cleaned = cleaned.removesuffix("'s")

    if cleaned in ("", "measurement"):
        return context.measurement

    aliases: dict[str, str] = {
        "task_a": "first_measurement",
        "task_b": "second_measurement",
        "fast_child_task": "child_task_fast_measurement",
        "slow_child_task": "child_task_slow_measurement",
        "idle_thread": "idle_thread_measurement",
        "idle_sleeping_thread": "idle_thread_measurement",
    }
    attr = aliases.get(cleaned, f"{cleaned}_measurement")
    return getattr(context, attr)


def _get_span_duration(measurement: timerun.Measurement, kind: str) -> int:
    """Get wall or CPU time duration from a measurement."""
    span = getattr(measurement, f"{kind.lower()}_time")
    assert span is not None, f"Measurement has no {kind} time span"
    return span.duration


def _extract_timer_kwargs(context: Context) -> dict[str, Any]:
    """Extract timer keyword arguments from context."""
    kwargs: dict[str, Any] = {}
    if hasattr(context, "metadata"):
        kwargs["metadata"] = context.metadata
    if hasattr(context, "on_start_callback"):
        kwargs["on_start"] = context.on_start_callback
    if hasattr(context, "on_end_callback"):
        kwargs["on_end"] = context.on_end_callback
    return kwargs


def _run_timed_async_fn(
    kwargs: dict[str, Any],
    sleep_ns: int,
) -> tuple[object, timerun.Measurement]:
    """Create and run timed async function."""

    @timerun.Timer(**kwargs)
    async def async_fn() -> None:
        if sleep_ns:
            await asyncio.sleep(sleep_ns / 1e9)

    asyncio.run(async_fn())
    return async_fn, async_fn.measurements[-1]


def _run_timed_sync_fn(
    kwargs: dict[str, Any],
    sleep_ns: int,
) -> tuple[object, timerun.Measurement]:
    """Create and run timed sync function."""

    @timerun.Timer(**kwargs)
    def sync_fn() -> None:
        if sleep_ns:
            time.sleep(sleep_ns / 1e9)

    sync_fn()
    return sync_fn, sync_fn.measurements[-1]


# --- Given ---


@given("a {kind} function that sleeps for {duration_ns:n} nanoseconds")
@given("an {kind} function that sleeps for {duration_ns:n} nanoseconds")
def step_given_func_sleep(
    context: Context,
    kind: str,
    duration_ns: int,
) -> None:
    """Store func kind and duration."""
    context.func_duration_ns = duration_ns
    context.func_kind = kind


# --- When ---


@when("I measure a code block")
def step_measure_code_block(context: Context) -> None:
    """Measure a code block with options configured on context."""
    kwargs = _extract_timer_kwargs(context)
    try:
        with timerun.Timer(**kwargs) as context.measurement:
            pass
    # pylint: disable-next=broad-exception-caught
    except Exception as exc:  # noqa: BLE001
        context.exception = exc


@when("I measure two sequential blocks with the same Timer instance")
def step_measure_two_sequential_blocks(context: Context) -> None:
    """Measure two sequential blocks with a shared Timer."""
    kwargs: dict[str, Any] = {}
    if hasattr(context, "metadata"):
        kwargs["metadata"] = context.metadata
    cm = timerun.Timer(**kwargs)

    with cm as context.first_measurement:
        if hasattr(context, "metadata_add_in_first"):
            k, v = context.metadata_add_in_first
            context.first_measurement.metadata[k] = v
        if hasattr(context, "first_block_ns"):
            time.sleep(context.first_block_ns / 1e9)

    with cm as context.second_measurement:
        if hasattr(context, "second_block_ns"):
            time.sleep(context.second_block_ns / 1e9)


@when("I call the decorated function")
def step_call_decorated_function(context: Context) -> None:
    """Decorate and call a function with context options."""
    kwargs = _extract_timer_kwargs(context)
    sleep_ns = getattr(context, "func_duration_ns", 0)
    is_async = getattr(context, "func_kind", "sync") == "async"
    runner = _run_timed_async_fn if is_async else _run_timed_sync_fn

    try:
        func, measurement = runner(kwargs, sleep_ns)
        context.decorated_function = func
        context.measurement = measurement
    # pylint: disable-next=broad-exception-caught
    except Exception as exc:  # noqa: BLE001
        context.exception = exc


# --- Then ---


@then("a {exception_type} is raised")
@then("an {exception_type} is raised")
def step_exception_raised(context: Context, exception_type: str) -> None:
    """Assert stored exception matches expected type."""
    assert hasattr(context, "exception"), "Expected an exception to be raised"
    exc = context.exception
    matched = type(exc).__name__ == exception_type or (
        hasattr(builtins, exception_type)
        and isinstance(exc, getattr(builtins, exception_type))
    )
    assert matched, f"Expected {exception_type}, got {type(exc).__name__}"


@then('the error message is "{message}"')
def step_error_message_is(context: Context, message: str) -> None:
    """Assert exception message."""
    assert hasattr(context, "exception"), "Expected an exception to be raised"
    assert str(context.exception) == message


@then(
    "the measurement's {kind} time duration is approximately "
    "{expected_ns:n} nanoseconds",
)
@then(
    "the {which} measurement's {kind} time duration is approximately "
    "{expected_ns:n} nanoseconds",
)
@then(
    "the {which}'s {kind} time duration is approximately "
    "{expected_ns:n} nanoseconds",
)
@then(
    "{which}'s {kind} time duration is approximately "
    "{expected_ns:n} nanoseconds",
)
def step_duration_approx(
    context: Context,
    kind: str,
    expected_ns: int,
    which: str | None = None,
) -> None:
    """Assert duration is within the expected tolerance buffer."""
    measurement = _measurement(context, which)
    duration = _get_span_duration(measurement, kind)
    if kind.lower() == "cpu":
        min_ns = max(0, expected_ns - CPU_TOLERANCE_NS)
    else:
        min_ns = expected_ns
    max_ns = expected_ns + BUFFER_NS

    assert min_ns <= duration <= max_ns, (
        f"{which or ''} {kind} time {duration} not in [{min_ns}, {max_ns}] "
        f"(buffer={BUFFER_NS})"
    )


@then(
    "the measurement's {kind} time duration is at least "
    "{expected_ns:n} nanoseconds",
)
@then(
    "the {which} measurement's {kind} time duration is at least "
    "{expected_ns:n} nanoseconds",
)
@then(
    "the {which}'s {kind} time duration is at least "
    "{expected_ns:n} nanoseconds",
)
@then(
    "{which}'s {kind} time duration is at least {expected_ns:n} nanoseconds",
)
def step_duration_at_least(
    context: Context,
    kind: str,
    expected_ns: int,
    which: str | None = None,
) -> None:
    """Assert duration is at least expected bound."""
    measurement = _measurement(context, which)
    duration = _get_span_duration(measurement, kind)
    assert duration >= expected_ns, (
        f"{which or ''} {kind} time {duration} < {expected_ns}"
    )


@then(
    "the measurement's {kind} time duration is at most "
    "{expected_ns:n} nanoseconds",
)
@then(
    "the {which} measurement's {kind} time duration is at most "
    "{expected_ns:n} nanoseconds",
)
@then(
    "the {which}'s {kind} time duration is at most "
    "{expected_ns:n} nanoseconds",
)
@then(
    "{which}'s {kind} time duration is at most {expected_ns:n} nanoseconds",
)
def step_duration_at_most(
    context: Context,
    kind: str,
    expected_ns: int,
    which: str | None = None,
) -> None:
    """Assert duration is at most expected bound."""
    measurement = _measurement(context, which)
    duration = _get_span_duration(measurement, kind)
    assert duration <= expected_ns, (
        f"{which or ''} {kind} time {duration} > {expected_ns}"
    )


@then("the measurement's {kind} time duration is {expected_ns:n} nanoseconds")
@then(
    "the {which} measurement's {kind} time duration is {expected_ns:n} "
    "nanoseconds",
)
@then(
    "the {which}'s {kind} time duration is {expected_ns:n} nanoseconds",
)
@then(
    "{which}'s {kind} time duration is {expected_ns:n} nanoseconds",
)
def step_duration_exact(
    context: Context,
    kind: str,
    expected_ns: int,
    which: str | None = None,
) -> None:
    """Assert duration equals expected exactly."""
    measurement = _measurement(context, which)
    duration = _get_span_duration(measurement, kind)
    assert duration == expected_ns, (
        f"{which or ''} {kind} time {duration} != {expected_ns}"
    )


@then("the measurement includes metadata:")
@then("the {which} measurement includes metadata:")
def step_measurement_includes_metadata_table(
    context: Context,
    which: str | None = None,
) -> None:
    """Assert measurement metadata contains all key/value pairs in table."""
    measurement = _measurement(context, which)
    for row in context.table:
        key, expected_val = row["key"], row["value"]
        assert key in measurement.metadata, (
            f"Key {key!r} not found in metadata"
        )
        assert measurement.metadata[key] == expected_val, (
            f"Expected metadata[{key!r}] == {expected_val!r}, "
            f"got {measurement.metadata[key]!r}"
        )


@then('the measurement does not include metadata key "{key}"')
@then('the {which} measurement does not include metadata key "{key}"')
def step_measurement_excludes_metadata_key(
    context: Context,
    key: str,
    which: str | None = None,
) -> None:
    """Assert measurement metadata does not contain key."""
    measurement = _measurement(context, which)
    assert key not in measurement.metadata, (
        f"Key {key!r} unexpectedly found in metadata"
    )


@then("the decorated function has recorded {n:n} measurement")
@then("the decorated function has recorded {n:n} measurements")
def step_then_measurements_count(context: Context, n: int) -> None:
    """Assert measurements count is n."""
    func = context.decorated_function
    assert len(func.measurements) == n, (
        f"expected {n} measurements, got {len(func.measurements)}"
    )
