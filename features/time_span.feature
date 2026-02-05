Feature: Time span
  As someone measuring how long something takes,
  I want a span of time that tells me how long it took,
  so that I can:
    - compare which took longer
    - see the duration in a familiar form (e.g. seconds)
    - tell which started or ended first

  Scenario: I can see how long the span is
    Given a time span from 0 to 1,000,000
    Then the duration is 1,000,000 nanoseconds

  Scenario: I can see the duration in a standard form
    Given a time span from 0 to 2,500,000,000
    Then the timedelta is 2.5 seconds in standard Python timedelta type

  Scenario Outline: I can compare spans by duration
    Given span A of <duration_a> nanoseconds
    And span B of <duration_b> nanoseconds
    Then time span A <relation> time span B

    Examples:
      | duration_a | duration_b | relation                    |
      | 1,000,000  | 2,000,000  | is less than                |
      | 3,000,000  | 1,000,000  | is greater than             |
      | 1,000,000  | 1,000,000  | equals                      |
      | 1,000,000  | 2,000,000  | does not equal              |
      | 1,000,000  | 1,000,000  | is less than or equal to    |
      | 2,000,000  | 1,000,000  | is greater than or equal to |

  Scenario: I can read start and end
    Given a time span from 1,000 to 2,000
    Then the start value is 1,000
    And the end value is 2,000
