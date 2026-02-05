Feature: Measurement record

  As someone measuring how long something takes,
  I want a measurement record with wall time, CPU time, and optional metadata,
  so that I can:
    - store and pass around timing results in a structured way
    - read wall and CPU durations from that record
    - attach metadata (e.g. tags, run id) to label or correlate runs

  Scenario: I can create a measurement from wall and CPU time spans and see the durations
    Given a wall time span from 0 to 1,000,000
    And a CPU time span from 0 to 500,000
    When I create a measurement from the wall time span and the CPU time span
    Then the measurement's wall time duration is 1,000,000 nanoseconds
    And the measurement's CPU time duration is 500,000 nanoseconds

  Scenario: I can see that a new measurement's metadata is an empty dict
    Given a wall time span from 0 to 1
    And a CPU time span from 0 to 1
    When I create a measurement from the wall time span and the CPU time span
    Then the measurement's metadata is an empty dict

  Scenario: I can set metadata on a measurement and read it back
    Given a wall time span from 0 to 1
    And a CPU time span from 0 to 1
    When I create a measurement from the wall time span and the CPU time span
    And the metadata key "run_id" is set to "exp-1"
    And the metadata key "tag" is set to "baseline"
    Then the measurement's metadata key "run_id" is "exp-1"
    And the measurement's metadata key "tag" is "baseline"
