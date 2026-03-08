Feature: Block timing

  As someone measuring duration,
  I want to time blocks of code (sync, async, or threaded),
  so that I get per-task timings and can attach metadata.

  # --- Basic timing: sync, async, CPU-bound ---

  Scenario: Blocking sleep with `with` yields wall time and near-zero CPU time
    Given a blocking operation that runs for around 10,000,000 nanoseconds
    When I measure the operation using `with`
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: Async sleep with `async with` yields wall time and near-zero CPU time
    Given an async operation that runs for around 10,000,000 nanoseconds
    When I measure the async operation using `async with`
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 0 nanoseconds

  Scenario: CPU-bound block with `with` yields wall and CPU time close together
    Given a CPU-bound operation that runs for around 10,000,000 nanoseconds
    When I measure the operation using `with`
    Then the measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time duration is within the configured buffer of 10,000,000 nanoseconds
    And the measurement's CPU time is close to wall time

  # --- One Timer, multiple blocks or threads ---

  Scenario: Two threads with one Timer yield one measurement per thread
    Given each thread sleeps 5,000,000 nanoseconds
    When I measure blocks from 2 threads using the same Timer instance
    Then the measurements are from different threads

  Scenario: Two sequential blocks with one Timer yield correct durations
    Given the first block duration is 5,000,000 nanoseconds
    And the second block duration is 10,000,000 nanoseconds
    When I measure two sequential blocks with the same Timer instance
    Then the first measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the second measurement's wall time duration is within the configured buffer of 10,000,000 nanoseconds

  Scenario: Nested blocks with one Timer yield independent outer and inner times
    Given the outer block duration is 20,000,000 nanoseconds
    And the inner block duration is 5,000,000 nanoseconds
    When I measure nested blocks with the same Timer instance
    Then the outer measurement's wall time duration is within the configured buffer of 25,000,000 nanoseconds
    And the inner measurement's wall time duration is within the configured buffer of 5,000,000 nanoseconds
    And the outer measurement's wall time duration is at least the inner measurement's wall time duration

  # --- Metadata ---

  Scenario: Initial metadata is carried on the yielded measurement
    Given metadata run_id "exp-1" and tag "baseline"
    When I measure a code block with that metadata
    Then the measurement's metadata key "run_id" is "exp-1"
    And the measurement's metadata key "tag" is "baseline"

  Scenario: Metadata set in first block is not visible in second block (reused Timer)
    Given metadata run_id "same-run" and tag "original"
    And I will add metadata key "extra" as "from_first_block" in the first block
    When I measure two blocks with the same Timer instance and that metadata
    Then the first measurement's metadata key "extra" is "from_first_block"
    And the second measurement's metadata key "run_id" is "same-run"
    And the second measurement's metadata key "tag" is "original"
    And the second measurement's metadata does not contain key "extra"

  # --- Callbacks on start and end ---

  Scenario: The on_start callback is invoked once with the same measurement instance the Timer yields for that block
    Given an on_start callback that records invocations
    When I measure a code block with a Timer that has that on_start callback
    Then the on_start callback was called once
    And the on_start callback was called with the same measurement instance that the Timer yielded for that block

  Scenario: The on_end callback is invoked once with the same measurement instance the Timer yields for that block
    Given an on_end callback that records invocations
    When I measure a code block with a Timer that has that on_end callback
    Then the on_end callback was called once
    And the on_end callback was called with the same measurement instance that the Timer yielded for that block

  # --- Edge cases and errors ---

  Scenario: Block that raises still yields measurement; exception propagates
    When I measure a code block that raises an exception
    Then the block yielded a measurement
    And an exception was propagated to the caller

  Scenario: __exit__ without __enter__ raises RuntimeError
    When I call __exit__ on a Timer instance without calling __enter__ first
    Then a RuntimeError is raised
    And the error message is "__exit__ called without a matching __enter__"
