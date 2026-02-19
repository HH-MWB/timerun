Feature: Time span

  As someone measuring duration,
  I want a time span,
  so that I can compare durations, use timedelta, and read start or end.

  # --- Duration and attributes ---

  Scenario: Span duration is readable in nanoseconds
    Given a time span from 0 to 1,000,000
    Then the duration is 1,000,000 nanoseconds

  Scenario: Span start and end are readable
    Given a time span from 1,000 to 2,000
    Then the start value is 1,000
    And the end value is 2,000

  Scenario: Duration as standard Python timedelta
    Given a time span from 0 to 2,500,000,000
    Then the timedelta is 2.5 seconds in standard Python timedelta type

  # --- Comparison ---

  Scenario Outline: Compare two spans by duration
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

  # --- Validation ---

  Scenario: end less than start raises ValueError
    When I try to create a time span from 10 to 5
    Then a ValueError is raised
    And the error message is "end must be >= start"
