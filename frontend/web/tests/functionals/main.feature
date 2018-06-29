Feature: Basic use of IRMA

  Scenario: As an user, I can scan a file
    Given I am on the main page
    When I select a malware
    And I click on "Scan for malwares"
    Then The page title should be "IRMA | Upload"
    When I wait for the upload to finish
    Then The page title should be "IRMA | Scan"
    When I wait for the scan to finish
    Then The file "eicar.com" should be flagged as a malware

  # `@newPage` is only there as an example, but this is not mandatory for every
  # scenario if you don't want to open a new tab/page
  @newPage
  Scenario: As an user, I can search for a file
    Given I am on the main page
    When I click on "Search"
    And I wait to see a search result
    Then The page title should be "IRMA | Search"
    When I type "eicar" in the search input
    And I click on "Go!"
    And I wait to see a search result
    Then I should see "eicar.com" in the search results
