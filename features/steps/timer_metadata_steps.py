"""Step definitions for Timer metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, then, when

import timerun

if TYPE_CHECKING:
    from behave.runner import Context


# --- Given ---


@given('metadata run_id "{run_id}" and tag "{tag}"')
def step_given_metadata(context: Context, run_id: str, tag: str) -> None:
    """Store metadata for Timer."""
    context.metadata = {"run_id": run_id, "tag": tag}


@given('I will add metadata key "{key}" as "{value}" in the first block')
def step_given_metadata_add_in_first(
    context: Context,
    key: str,
    value: str,
) -> None:
    """First block will add key/value to metadata."""
    context.metadata_add_in_first = (key, value)


# --- When ---


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


@when("I call a decorated function with that metadata")
def step_when_call_with_metadata(context: Context) -> None:
    """Call no-op function decorated with Timer(metadata=...)."""

    @timerun.Timer(metadata=context.metadata)
    def f() -> None:
        pass

    f()
    context.decorated_function = f
    context.measurement = f.measurements[-1]


# --- Then ---


@then('the second measurement\'s metadata does not contain key "{key}"')
def step_second_measurement_metadata_no_key(
    context: Context,
    key: str,
) -> None:
    """Assert second measurement has no key."""
    assert key not in context.second_measurement.metadata
