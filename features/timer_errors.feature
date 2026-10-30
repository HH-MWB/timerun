Feature: Timer error handling

  As a developer writing resilient systems,
  I want timing to handle errors gracefully and fail fast on misuse,
  so that failing operations capture timings and misuse is clearly reported.

  Scenario: Block that raises an exception still yields a measurement
    When I measure a code block that raises an exception
    Then the block yielded a measurement
    And a ValueError is raised

  Scenario: Timed function that raises still records measurement
    When I call the decorated function that raises an exception
    Then the decorated function has recorded 1 measurement
    And a ValueError is raised

  Scenario: Exiting an un-entered timer raises RuntimeError
    Given a Timer that has not been entered
    When I exit the timer
    Then a RuntimeError is raised
    And the error message is "__exit__ called without a matching __enter__"

  Scenario: Measuring asynchronously without an active task raises RuntimeError
    Given an event loop where code runs with no current asyncio task
    When I use async with Timer from a callback on that loop
    Then a RuntimeError is raised
    And the error message is "no current asyncio task"

  Scenario: Callback on_start that raises an exception propagates cleanly
    Given an on_start callback that raises an application exception
    When I call the decorated function
    Then a CustomAppError is raised

  Scenario: Callback on_end that raises an exception propagates cleanly
    Given an on_end callback that raises an application exception
    When I measure a code block
    Then a CustomAppError is raised
