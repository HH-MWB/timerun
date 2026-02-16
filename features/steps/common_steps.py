"""Shared step definitions used by multiple features.

Steps here use consistent wording and semantics across features
(exception assertions, error messages, measurement metadata).
"""

import builtins

from behave import then
from behave.runner import Context


@then("a {exception_type} is raised")
def step_exception_raised(context: Context, exception_type: str) -> None:
    """Assert exception of the given type was stored in context.exception."""
    assert hasattr(context, "exception"), "Expected an exception to be raised"
    assert isinstance(context.exception, getattr(builtins, exception_type)), (
        f"Expected {exception_type}, got {type(context.exception).__name__}"
    )


@then('the error message is "{message}"')
def step_error_message_is(context: Context, message: str) -> None:
    """Assert the stored exception message equals message."""
    assert hasattr(context, "exception"), "Expected an exception to be raised"
    assert str(context.exception) == message


@then('the measurement\'s metadata key "{key}" is "{value}"')
def step_measurement_metadata_key_is(
    context: Context,
    key: str,
    value: str,
) -> None:
    """Assert the key value pair is in measurement's metadata."""
    assert context.measurement.metadata[key] == value
