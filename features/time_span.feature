Feature: Time span

  As a developer analyzing elapsed intervals,
  I want an immutable nanosecond time span with timedelta conversion,
  so that I can accurately calculate durations and compare timestamps.

  Scenario: Time span encapsulates start, end, and duration in nanoseconds
    Given a time span from 1,000 to 2,000
    Then the start value is 1,000
    And the end value is 2,000
    And the duration is 1,000 nanoseconds

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

  Scenario: Spans are ordered by comparing their duration properties
    Given span A with duration 1,000,000 nanoseconds
    And span B with duration 2,000,000 nanoseconds
    Then time span A's duration is less than time span B's duration

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
    Then modifying the time span is rejected
