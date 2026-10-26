Feature: Timer callbacks

  As someone measuring duration,
  I want callbacks when timing starts and ends,
  so that I can react to measurement lifecycle events.

  Scenario Outline: Lifecycle callback is invoked once with the yielded measurement
    Given an <callback_name> callback that records invocations
    When I measure a code block
    Then the <callback_name> callback was called once
    And the <callback_name> callback received the yielded measurement

    Examples:
      | callback_name |
      | on_start      |
      | on_end        |

  Scenario: Both on_start and on_end callbacks are invoked for a measured block
    Given an on_start callback that records invocations
    And an on_end callback that records invocations
    When I measure a code block
    Then the on_start callback was called once
    And the on_end callback was called once
    And both callbacks received the yielded measurement

  Scenario: Timing spans are unset during on_start and set during on_end
    Given an on_start callback that records timing state
    And an on_end callback that records timing state
    When I measure a code block
    Then the measurement recorded by on_start had no timing spans
    And the measurement recorded by on_end had valid timing spans
