Feature: Basic timing

  As someone measuring duration,
  I want to time code execution (blocks, functions, and generators),
  so that I get accurate wall time and CPU time measurements.

  Scenario: Measuring synchronous blocking operation yields wall time and minimal CPU time
    Given a blocking operation that runs for 5,000,000 nanoseconds
    When I measure the operation
    Then the measurement's wall time duration is approximately 5,000,000 nanoseconds
    And the measurement's CPU time duration is approximately 0 nanoseconds

  Scenario: Measuring asynchronous operation yields wall time and minimal CPU time
    Given an async operation that runs for 5,000,000 nanoseconds
    When I measure the operation
    Then the measurement's wall time duration is approximately 5,000,000 nanoseconds
    And the measurement's CPU time duration is approximately 0 nanoseconds

  Scenario: Measuring CPU-bound operation records both wall time and CPU time
    Given a CPU-bound operation that runs for 5,000,000 nanoseconds
    When I measure the operation
    Then the measurement's wall time duration is at least 5,000,000 nanoseconds
    And the measurement's CPU time duration is approximately 5,000,000 nanoseconds

  Scenario Outline: Timing a <mode> sleeping function records wall time and minimal CPU time
    Given a <mode> function that sleeps for 5,000,000 nanoseconds
    When I call the decorated function
    Then the measurement's wall time duration is approximately 5,000,000 nanoseconds
    And the measurement's CPU time duration is approximately 0 nanoseconds

    Examples:
      | mode  |
      | sync  |
      | async |

  Scenario Outline: Fully consuming a <mode> generator records one measurement
    Given a <mode> generator that yields 3 items and sleeps 2,500,000 nanoseconds total
    When I fully consume the decorated generator
    Then the decorated function has recorded 1 measurement

    Examples:
      | mode  |
      | sync  |
      | async |

  Scenario: Partially consuming a generator records one measurement
    Given a sync generator that yields 5 items and sleeps 2,000,000 nanoseconds total
    When I consume only 2 items from the decorated generator
    Then the decorated function has recorded 1 measurement

  Scenario: Decorating a function preserves its return type
    Given a function with a typed return signature
    When I decorate the function with Timer
    Then the decorated function preserves the original return type
