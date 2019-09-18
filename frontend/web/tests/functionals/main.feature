Feature: Basic use of IRMA

  Scenario: As a user, I cannot launch a scan with no valid file
    Given I am on the main page
    Then The button "Scan for malwares" is not enabled
    # Allow to select the folder "/" referenced in the step
    # As folders are not allowed in the upload component
    # it will launch the upload and reject the folder
    When I select the file named ""
    When I wait for the upload to finish
    Then I should see a "danger" alert
    Then The button "Scan for malwares" is not enabled

  Scenario: As a user, I can scan a file and download the report
    Given I am on the main page
    When I select the file named "eicar.com"
    And I select the file named "hello_world.txt"
    When I wait for the upload to finish
    Then The button "Scan for malwares" is enabled
    And I click on "Scan for malwares"
    Then The page title should be "IRMA | Scan"
    When I wait for the scan to finish
    Then The file "eicar.com" should be flagged as a malware
    And The file "hello_world.txt" should not be flagged as a malware
    When I click on "csv"
    Then I should be able to download the csv report
    When I click on "eicar.com"
    Then The page title should be "IRMA | Results"

  # `@newPage` can be used if you want to open a new tab/page
  #@newPage
  Scenario: As a user, I can access the search page
    Given I am on the main page
    When I click on "Search"
    Then The page title should be "IRMA | Search"
    And I should see "eicar.com" in the search results
    And I should see "hello_world.txt" in the search results

  Scenario: As a user, when I access a result from the search page and go
        back, I want to keep search informations
    Given I am on the search page
    When I type "eicar" in the search input
    And I click on "Go!"
    Then I should not see "hello_world.txt" in the search results
    When I click on "eicar.com"
    Then The page title should be "IRMA | Results"
    When I go back
    Then I should see "eicar.com" in the search results
    And I should not see "hello_world.txt" in the search results

  Scenario: As a user, When I enter a search URL, and should be able to see
        the rights results
    Given I am on the previous_searched page
    Then I should see "eicar.com" in the search results
    And I should not see "hello_world.txt" in the search results
