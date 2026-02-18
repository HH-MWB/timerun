"""Shared utilities for step definitions.

Constants and helpers for block_timing_steps and function_timing_steps
to avoid duplication and keep assertions consistent.
"""

import time

# Buffer: expected_ns <= duration <= expected_ns + BUFFER_NS.
# Covers sleep/scheduling jitter so tests don't flake.
BUFFER_NS = 10_000_000  # 10 ms

# CPU can be slightly below wall time (scheduling); allow 1 ms undershoot.
CPU_LOWER_SLACK_NS = 1_000_000


def sleep_wall_at_least(nanoseconds: int) -> None:
    """Sleep at least nanoseconds (wall)."""
    time.sleep(nanoseconds / 1e9)


def spin_wall_at_least(nanoseconds: int) -> None:
    """Busy-loop at least nanoseconds (wall)."""
    start = time.perf_counter_ns()
    while time.perf_counter_ns() - start < nanoseconds:
        pass


def assert_wall_time_within_buffer(
    measurement: object,
    expected_ns: int,
    buffer_ns: int = BUFFER_NS,
) -> None:
    """Assert wall time in buffer."""
    assert measurement.wall_time is not None
    duration = measurement.wall_time.duration
    max_ns = expected_ns + buffer_ns
    assert expected_ns <= duration <= max_ns, (
        f"wall time {duration} not in [{expected_ns}, {max_ns}] "
        f"(buffer={buffer_ns})"
    )


def assert_metadata_key_equals(
    measurement: object,
    key: str,
    value: str,
) -> None:
    """Assert metadata[key] equals value."""
    assert measurement.metadata[key] == value
