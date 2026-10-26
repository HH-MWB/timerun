Feature: Time span

  As someone measuring duration,
  I want a time span,
  so that I can compare durations, use timedelta, and read start or end.

  Scenario: Span duration is readable in nanoseconds
    Given a time span from 0 to 1,000,000
    When I read the duration
    Then the duration is 1,000,000 nanoseconds

  Scenario: Span start and end are readable
    Given a time span from 1,000 to 2,000
    When I read the start and end values
    Then the start value is 1,000
    And the end value is 2,000

  Scenario: Span duration is readable as a timedelta
    Given a time span from 0 to 2,500,000,000
    When I read the duration as a timedelta
    Then the timedelta is 2.5 seconds

  Scenario: Nanoseconds are truncated to whole microseconds for timedelta
    Given a time span from 0 to 1,500
    When I read the duration as a timedelta
    Then the timedelta is 0.000001 seconds

  Scenario: Distinct time spans with identical durations do not compare equal
    Given a time span A from 1,000,000,000 to 1,500,000,000
    And a time span B from 100,000,000,000 to 100,500,000,000
    When I compare time span A and time span B
    Then time span A does not equal time span B
    And both spans are distinct when collected in a set

  Scenario Outline: Compare two spans by duration
    Given span A with duration <duration_a> nanoseconds
    And span B with duration <duration_b> nanoseconds
    When I compare the durations of span A and span B
    Then time span A's duration <relation> time span B's duration

    Examples:
      | duration_a | duration_b | relation                    |
      | 1,000,000  | 2,000,000  | is less than                |
      | 3,000,000  | 1,000,000  | is greater than             |
      | 1,000,000  | 1,000,000  | equals                      |
      | 1,000,000  | 2,000,000  | does not equal              |
      | 1,000,000  | 1,000,000  | is less than or equal to    |
      | 2,000,000  | 1,000,000  | is greater than or equal to |

  Scenario: End timestamp earlier than start raises ValueError
    When I try to create a time span from 10 to 5
    Then a ValueError is raised
    And the error message is "end must be >= start"

  Scenario Outline: Unsupported ordering comparisons raise TypeError
    Given a time span from 0 to 1,000,000
    When I compare whether the time span is less than <operand>
    Then a TypeError is raised

    Examples:
      | operand           |
      | an integer        |
      | a float           |
      | a string          |
      | another time span |

  Scenario: Time span attributes cannot be modified
    Given a time span from 0 to 1,000,000
    When I try to modify the start value
    Then a FrozenInstanceError is raised
