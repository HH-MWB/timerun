"""Step definitions for Timer metadata."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from behave import given, then

if TYPE_CHECKING:
    from behave.runner import Context

# --- Given ---


@given("initial metadata:")
def step_given_metadata_table(context: Context) -> None:
    """Store metadata for Timer from table."""
    context.metadata = {row["key"]: row["value"] for row in context.table}


@given("metadata with an unpickleable lock object")
def step_metadata_unpickleable_lock(context: Context) -> None:
    """Store metadata containing a threading.Lock."""
    context.lock_obj = threading.Lock()
    context.metadata = {"lock": context.lock_obj}


@given('the first block adds metadata key "{key}" with value "{value}"')
def step_given_metadata_add_in_first(
    context: Context,
    key: str,
    value: str,
) -> None:
    """First block will add key/value to metadata."""
    context.metadata_add_in_first = (key, value)


# --- When ---
# Actions for this feature use shared steps in common_steps.py
# (e.g. "When I measure a code block").


# --- Then ---


@then("the measurement completes successfully")
def step_measurement_completes_successfully(context: Context) -> None:
    """Assert measurement completed and is set on context."""
    assert hasattr(context, "measurement")
    assert context.measurement is not None


@then("the measurement metadata carries the lock object")
def step_measurement_carries_lock(context: Context) -> None:
    """Assert measurement metadata holds the original lock object."""
    assert context.measurement.metadata.get("lock") is context.lock_obj
