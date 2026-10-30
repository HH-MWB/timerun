Feature: Timer metadata

  As a developer analyzing benchmark runs,
  I want to attach contextual metadata to timers and measurements,
  so that I can correlate timings with request IDs and test parameters.

  Scenario: Initial metadata is carried on the yielded measurement
    Given initial metadata:
      | key    | value    |
      | run_id | exp-1    |
      | tag    | baseline |
    When I measure a code block
    Then the measurement includes metadata:
      | key    | value    |
      | run_id | exp-1    |
      | tag    | baseline |

  Scenario: Metadata attached to the timer appears on each measurement
    Given initial metadata:
      | key    | value    |
      | run_id | exp-1    |
      | tag    | baseline |
    When I call the decorated function
    Then the measurement includes metadata:
      | key    | value    |
      | run_id | exp-1    |
      | tag    | baseline |

  Scenario: Metadata set in first block is not visible in second block with reused Timer
    Given initial metadata:
      | key    | value    |
      | run_id | same-run |
      | tag    | original |
    And the first block adds metadata key "extra" with value "from_first_block"
    When I measure two sequential blocks with the same Timer instance
    Then the first measurement includes metadata:
      | key   | value            |
      | extra | from_first_block |
    And the second measurement includes metadata:
      | key    | value    |
      | run_id | same-run |
      | tag    | original |
    And the second measurement does not include metadata key "extra"

  Scenario: Metadata containing synchronization objects does not crash on enter
    Given metadata with an unpickleable lock object
    When I measure a code block
    Then the measurement completes successfully
    And the measurement metadata carries the lock object
