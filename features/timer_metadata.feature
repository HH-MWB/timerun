Feature: Timer metadata

  As someone measuring duration,
  I want to attach metadata to measurements,
  so that I can label and identify results.

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

  Scenario: Metadata attached to the timer appears on each measurement
    Given metadata run_id "exp-1" and tag "baseline"
    When I call a decorated function with that metadata
    Then the measurement's metadata key "run_id" is "exp-1"
    And the measurement's metadata key "tag" is "baseline"
