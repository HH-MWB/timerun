Feature: Package version

  As a user or tool integrating with timerun,
  I want to read the package version programmatically,
  so that I can check compatibility, display it to users, or use it in automation.

  Scenario: Package exposes a readable version
    When I read the package version
    Then the package has a version
    And the version is a non-empty string
