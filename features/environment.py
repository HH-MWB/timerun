"""Behave environment hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from behave.model import Scenario
    from behave.runner import Context


def before_scenario(context: Context, _: Scenario) -> None:
    """Reset context attributes before each scenario."""
    context.measurement = None
    context.exception = None


def after_scenario(context: Context, _: Scenario) -> None:
    """Clean up open resources after each scenario."""
    if hasattr(context, "loop") and not context.loop.is_closed():
        context.loop.close()
