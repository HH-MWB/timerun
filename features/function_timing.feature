Feature: Function timing

  As someone measuring duration,
  I want to time function and generator execution with a decorator,
  so that I get per-call measurements and can attach metadata.

  # --- Sync and async functions ---

  Scenario: Timing a synchronous sleeping function records real time and minimal CPU time
    Given a sync function that sleeps for around 10,000,000 nanoseconds
    When I call the decorated sync function
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: Timing an async sleeping function records real time and minimal CPU time
    Given an async function that sleeps for around 10,000,000 nanoseconds
    When I call the decorated async function
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  # --- Sync and async generators ---

  Scenario: Fully consuming a sync generator records one measurement
    Given a sync generator that yields 3 items and sleeps 5,000,000 nanoseconds total
    When I fully consume the decorated sync generator
    Then the decorated function's measurements deque has 1 entry

  Scenario: Fully consuming an async generator records one measurement
    Given an async generator that yields 3 items and sleeps 5,000,000 nanoseconds total
    When I fully consume the decorated async generator
    Then the decorated function's measurements deque has 1 entry

  # --- Metadata ---

  Scenario: Metadata attached to the timer appears on each measurement
    Given metadata run_id "exp-1" and tag "baseline"
    When I call a decorated function with that metadata
    Then the measurement's metadata key "run_id" is "exp-1"
    And the measurement's metadata key "tag" is "baseline"

  # --- Exceptions ---

  Scenario: When a timed function raises an error, one measurement is still recorded and the error is re-raised
    When I call a decorated function that raises an exception
    Then the decorated function's measurements deque has 1 entry
    And an exception was propagated to the caller

  # --- Limiting stored measurements (maxlen) ---

  Scenario: With maxlen 2, only the last 2 measurements are kept
    Given a sync function that sleeps for around 1,000,000 nanoseconds
    When I decorate it with FunctionTimer with maxlen 2
    And I call the decorated function 3 times
    Then the decorated function's measurements deque has 2 entries

  # --- Thread safety ---

  Scenario: Two threads calling the same timed function produce two measurements
    Given a sync function that sleeps for around 5,000,000 nanoseconds
    When I call the decorated function from 2 threads concurrently
    Then the decorated function's measurements deque has 2 entries
