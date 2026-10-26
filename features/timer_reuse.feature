Feature: Timer reuse

  As someone measuring duration,
  I want to reuse one Timer across multiple executions,
  so that each execution is independently measured and storage stays bounded.

  Scenario: Two threads with one Timer yield one measurement per thread
    Given each thread sleeps 2,000,000 nanoseconds
    When I measure blocks from 2 threads using the same Timer instance
    Then the measurements are from different threads

  Scenario: Two sequential blocks with one Timer yield correct durations
    Given the first block duration is 2,000,000 nanoseconds
    And the second block duration is 5,000,000 nanoseconds
    When I measure two sequential blocks with the same Timer instance
    Then the first measurement's wall time duration is approximately 2,000,000 nanoseconds
    And the second measurement's wall time duration is approximately 5,000,000 nanoseconds

  Scenario: Nested blocks with one Timer yield independent outer and inner times
    Given the outer block duration is 10,000,000 nanoseconds
    And the inner block duration is 2,000,000 nanoseconds
    When I measure nested blocks with the same Timer instance
    Then the outer measurement's wall time duration is approximately 12,000,000 nanoseconds
    And the inner measurement's wall time duration is approximately 2,000,000 nanoseconds
    And the outer measurement's wall time duration is at least the inner measurement's wall time duration

  Scenario Outline: Concurrent tasks record accurate measurements regardless of task finish order
    Given a shared Timer
    And task A runs for <task_a_duration> nanoseconds
    And task B runs for <task_b_duration> nanoseconds
    And task A starts before task B
    When I run both tasks concurrently with the same Timer
    Then task A's wall time duration is approximately <task_a_duration> nanoseconds
    And task B's wall time duration is approximately <task_b_duration> nanoseconds

    Examples:
      | task_a_duration | task_b_duration |
      | 500,000         | 2,000,000       |
      | 2,000,000       | 500,000         |

  Scenario: Two threads calling the same timed function produce two measurements
    Given a sync function that sleeps for 2,000,000 nanoseconds
    When I call the decorated function from 2 threads concurrently
    Then the decorated function has recorded 2 measurements

  Scenario: With maxlen 2, only the last 2 measurements are kept
    Given a sync function that sleeps for 500,000 nanoseconds
    When I decorate the function with a Timer having maxlen 2
    And I call the decorated function 3 times
    Then the decorated function has recorded 2 measurements

  Scenario: Child tasks spawned inside an active timer measure independently
    Given a shared Timer
    And child task fast runs for 10,000,000 nanoseconds
    And child task slow runs for 50,000,000 nanoseconds
    When I run both child tasks concurrently from within the active outer timer
    Then the fast child task's wall time duration is at most 30,000,000 nanoseconds
    And the slow child task's wall time duration is at least 40,000,000 nanoseconds

  Scenario: Idle sleeping thread does not accumulate CPU time from concurrent thread
    Given a CPU-bound thread that runs for 100,000,000 nanoseconds
    And an idle sleeping thread that runs for 100,000,000 nanoseconds
    When I measure both threads concurrently with the same Timer instance
    Then the idle sleeping thread's CPU time duration is at most 25,000,000 nanoseconds
