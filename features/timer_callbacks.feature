Feature: Timer callbacks

  As someone measuring duration,
  I want callbacks when timing starts and ends,
  so that I can react to measurement lifecycle events.

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
