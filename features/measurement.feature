Feature: Measurement

  As someone measuring duration,
  I want a value with wall time, CPU time, and optional metadata,
  so that I can store results and attach labels.

  # --- Creating a measurement ---

  Scenario: Measurement from wall and CPU spans has both durations
    Given a wall time span from 0 to 1,000,000
    And a CPU time span from 0 to 500,000
    When I create a measurement from the wall time span and the CPU time span
    Then the measurement's wall time duration is 1,000,000 nanoseconds
    And the measurement's CPU time duration is 500,000 nanoseconds

  Scenario: New measurement has empty metadata by default
    Given a wall time span from 0 to 1
    And a CPU time span from 0 to 1
    When I create a measurement from the wall time span and the CPU time span
    Then the measurement's metadata is an empty dict

  # --- Metadata ---

  Scenario: Metadata can be set and read back
    Given a wall time span from 0 to 1
    And a CPU time span from 0 to 1
    When I create a measurement from the wall time span and the CPU time span
    And the metadata key "run_id" is set to "exp-1"
    And the metadata key "tag" is set to "baseline"
    Then the measurement's metadata key "run_id" is "exp-1"
    And the measurement's metadata key "tag" is "baseline"
