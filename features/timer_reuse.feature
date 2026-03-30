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
    Then the first measurement's wall time duration is within the configured buffer of 2,000,000 nanoseconds
    And the second measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds

  Scenario: Nested blocks with one Timer yield independent outer and inner times
    Given the outer block duration is 10,000,000 nanoseconds
    And the inner block duration is 2,000,000 nanoseconds
    When I measure nested blocks with the same Timer instance
    Then the outer measurement's wall time duration is within the configured buffer of 12,000,000 nanoseconds
    And the inner measurement's wall time duration is within the configured buffer of 2,000,000 nanoseconds
    And the outer measurement's wall time duration is at least the inner measurement's wall time duration

  Scenario: The task that started first finishes first
    Given a Timer shared by both tasks
    And task A runs for 500,000 nanoseconds
    And task B runs for 2,000,000 nanoseconds
    And task A starts before task B
    When I run both tasks concurrently with the same Timer
    Then the first measurement's wall time duration is within the configured buffer of 500,000 nanoseconds
    And the second measurement's wall time duration is within the configured buffer of 2,000,000 nanoseconds

  Scenario: The task that started second finishes first
    Given a Timer shared by both tasks
    And task A runs for 2,000,000 nanoseconds
    And task B runs for 500,000 nanoseconds
    And task A starts before task B
    When I run both tasks concurrently with the same Timer
    Then the first measurement's wall time duration is within the configured buffer of 2,000,000 nanoseconds
    And the second measurement's wall time duration is within the configured buffer of 500,000 nanoseconds

  Scenario: Two threads calling the same timed function produce two measurements
    Given a sync function that sleeps for around 2,000,000 nanoseconds
    When I call the decorated function from 2 threads concurrently
    Then the decorated function's measurements deque has 2 entries

  Scenario: With maxlen 2, only the last 2 measurements are kept
    Given a sync function that sleeps for around 500,000 nanoseconds
    When I decorate it with Timer with maxlen 2
    And I call the decorated function 3 times
    Then the decorated function's measurements deque has 2 entries
