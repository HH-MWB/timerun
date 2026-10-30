Feature: Measurement

  As a developer collecting performance telemetry,
  I want a structured record combining wall time, CPU time, and metadata,
  so that I can inspect timing metrics and attach diagnostic tags.

  Scenario: Measurement from wall and CPU spans has both durations
    Given a wall time span from 0 to 1,000,000
    And a CPU time span from 0 to 500,000
    When I create a measurement from the wall time span and the CPU time span
    Then the measurement's wall time duration is 1,000,000 nanoseconds
    And the measurement's CPU time duration is 500,000 nanoseconds

  Scenario: New measurement has empty metadata by default
    Given a default measurement
    Then the measurement's metadata is empty

  Scenario: Metadata can be set and read back
    Given a default measurement
    When I set the measurement metadata:
      | key    | value    |
      | run_id | exp-1    |
      | tag    | baseline |
    Then the measurement includes metadata:
      | key    | value    |
      | run_id | exp-1    |
      | tag    | baseline |
