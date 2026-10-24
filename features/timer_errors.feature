Feature: Timer error handling

  As someone measuring duration,
  I want timing to handle errors gracefully,
  so that measurements are preserved and misuse is clearly reported.

  Scenario: Block that raises still yields measurement; exception propagates
    When I measure a code block that raises an exception
    Then the block yielded a measurement
    And an exception was propagated to the caller

  Scenario: __exit__ without __enter__ raises RuntimeError
    When I call __exit__ on a Timer instance without calling __enter__ first
    Then a RuntimeError is raised
    And the error message is "__exit__ called without a matching __enter__"

  Scenario: async with Timer when no current asyncio task raises RuntimeError
    Given an event loop where code runs with no current asyncio task
    When I use async with Timer from a callback on that loop
    Then a RuntimeError is raised
    And the error message is "no current asyncio task"

  Scenario: When a timed function raises an error, one measurement is still recorded and the error is re-raised
    When I call a decorated function that raises an exception
    Then the decorated function's measurements deque has 1 entry
    And an exception was propagated to the caller

  Scenario: When a decorated function's on_start callback raises an error, that error propagates cleanly
    Given an on_start callback that raises an application exception
    When I call a decorated function with that on_start callback
    Then the application exception is propagated to the caller
    And no UnboundLocalError is raised
