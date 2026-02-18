Feature: Block timing

  As someone measuring duration,
  I want to time blocks of code (sync, async, or threaded),
  so that I get per-task timings and can attach metadata.

  # --- Basic timing: sync, async, CPU-bound ---

  Scenario: Blocking sleep with `with` yields wall time and near-zero CPU time
    Given a blocking operation that takes around 10,000,000 nanoseconds
    When I measure the blocking operation using `with`
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: Async sleep with `async with` yields wall time and near-zero CPU time
    Given an async operation that takes around 10,000,000 nanoseconds
    When I measure the async operation using `async with`
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: CPU-bound block with `with` yields wall and CPU time close together
    Given a CPU-bound operation that runs for around 10,000,000 nanoseconds
    When I measure the CPU-bound operation using `with`
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time is close to wall time

  # --- One BlockTimer, multiple blocks or threads ---

  Scenario: Two threads with one BlockTimer yield one measurement per thread
    Given each thread sleeps 5,000,000 nanoseconds
    When I measure blocks from 2 threads using the same BlockTimer instance
    Then the measurements are from different threads

  Scenario: Two sequential blocks with one BlockTimer yield correct durations
    Given the first block duration is 5,000,000 nanoseconds
    And the second block duration is 10,000,000 nanoseconds
    When I measure two sequential blocks with the same BlockTimer instance
    Then the first measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the second measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds

  Scenario: Nested blocks with one BlockTimer yield independent outer and inner times
    Given the outer block duration is 20,000,000 nanoseconds
    And the inner block duration is 5,000,000 nanoseconds
    When I measure nested blocks with the same BlockTimer instance
    Then the outer measurement's wall time duration is within the configured buffer of 25,000,000 nanoseconds
    And the inner measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the outer measurement's wall time duration is at least the inner measurement's wall time duration

  # --- Metadata ---

  Scenario: Initial metadata is carried on the yielded measurement
    Given metadata run_id "exp-1" and tag "baseline"
    When I measure a code block with that metadata
    Then the measurement's metadata key "run_id" is "exp-1"
    And the measurement's metadata key "tag" is "baseline"

  Scenario: Metadata set in first block is not visible in second block (reused BlockTimer)
    Given metadata run_id "same-run" and tag "original"
    And I will add metadata key "extra" as "from_first_block" in the first block
    When I measure two blocks with the same BlockTimer instance and that metadata
    Then the first measurement's metadata key "extra" is "from_first_block"
    And the second measurement's metadata key "run_id" is "same-run"
    And the second measurement's metadata key "tag" is "original"
    And the second measurement's metadata does not contain key "extra"

  # --- Edge cases and errors ---

  Scenario: Block that raises still yields measurement; exception propagates
    When I measure a code block that raises an exception
    Then the block yielded a measurement
    And an exception was propagated to the caller

  Scenario: __exit__ without __enter__ raises RuntimeError
    When I call __exit__ on a BlockTimer instance without calling __enter__ first
    Then a RuntimeError is raised
    And the error message is "__exit__ called without a matching __enter__"
