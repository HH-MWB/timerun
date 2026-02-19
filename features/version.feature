Feature: Package version

  As a user or tool integrating with timerun,
  I want to read the package version programmatically,
  so that I can check compatibility or use it in automation.

  Scenario: Package version is readable
    When I read the package version
    Then the version is a non-empty string
