Feature: Basic timing

  As someone measuring duration,
  I want to time code execution (blocks, functions, and generators),
  so that I get accurate wall time and CPU time measurements.

  Scenario: Blocking sleep with `with` yields wall time and near-zero CPU time
    Given a blocking operation that runs for around 5,000,000 nanoseconds
    When I measure the operation using `with`
    Then the measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: Async sleep with `async with` yields wall time and near-zero CPU time
    Given an async operation that runs for around 5,000,000 nanoseconds
    When I measure the async operation using `async with`
    Then the measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: CPU-bound block with `with` yields meaningful wall and CPU time
    Given a CPU-bound operation that runs for around 5,000,000 nanoseconds
    When I measure the operation using `with`
    Then the measurement's wall time duration is at least 5,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 5,000,000 nanoseconds

  Scenario: Timing a synchronous sleeping function records real time and minimal CPU time
    Given a sync function that sleeps for around 5,000,000 nanoseconds
    When I call the decorated function
    Then the measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: Timing an async sleeping function records real time and minimal CPU time
    Given an async function that sleeps for around 5,000,000 nanoseconds
    When I call the decorated function
    Then the measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: Fully consuming a sync generator records one measurement
    Given a sync generator that yields 3 items and sleeps 2,500,000 nanoseconds total
    When I fully consume the decorated generator
    Then the decorated function's measurements deque has 1 entry

  Scenario: Fully consuming an async generator records one measurement
    Given an async generator that yields 3 items and sleeps 2,500,000 nanoseconds total
    When I fully consume the decorated generator
    Then the decorated function's measurements deque has 1 entry
