Feature: Basic use of IRMA

  Scenario: As a user, I cannot launch a scan with no valid file
    # According to my understanding one scenario should have one expected result (Then condition). is should not be multiple when and then in same scenario
    Given I am on the main page
    # Since Given (Precondition) and repeatedly using in the test in that case we should write in Background: so that repetition of code can be avoid
    # Here when condition is missing
    # In Gherkin passing a parameter in single quote ''.
    Then The button "Scan for malwares" is not enabled
    # Allow to select the folder "/" referenced in the step
    # As folders are not allowed in the upload component
    # it will launch the upload and reject the folder

    # For good practice of gherkin language we should not use the key word I. Instead of I we can use "User can select the file name"
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

# According to my understanding I have written the same scenarios according to me below.

  Background:
    Given The user is on the main page

  Scenario: Verify button Scan for malwares is disabled
    When The home page is displayed correctly
    Then The button 'Scan for malwares' is 'disabled'

  Scenario: As a user, I cannot launch a scan with an invalid file
    When User selects the following file
      |file_name|
      |file1.xls|
    And Uploading file is completed
    Then Danger alert is displayed
    And The button 'Scan for malwares' is 'disabled'

  Scenario: Verification of single file upload
    When User selects the following file
      |file_name|
      |file1.xls|
    And Uploading file is completed
    Then The button "Scan for malwares" is 'enabled'
    And 1 'file is being uploaded' label is displayed

  Scenario: Verification of multiple files upload
    When User selects the following file
      |file_name|
      |file1.xls|
      |file2.xls|
    And Uploading file is completed
    Then The button "Scan for malwares" is 'enabled'
    And 2 'file is being uploaded' label is displayed

  Scenario: As a user, I can scan a file and download the report
    And User selects the following file
      |file_name|
      |file1.xls|
    And Uploading file is completed
    And The button 'Scan for malwares' is 'enabled'
    And 'Scan for malwares' button is clicked
    When scan status is in 'Finished' status
    And 'csv' button is clicked to download the report
    Then scan report is succcessfully downloaded
    And 'file1.xls' is selected in the download page under file details section
    And all file related informations are visible in the results page

  # `@newPage` can be used if you want to open a new tab/page
  #@newPage
  Scenario: As a user, I can access the search page
    When User able to click on 'Search' button
    Then The page title should be "IRMA | Search"
    And Verify that following search results displaying
      |Search Result  |
      |eicar.com      |
      |hello_world.txt|

  Scenario: As a user, when I access a result from the search page and go
  back, I want to keep search information
    When User type 'eicar' in the search input
    And User click on 'Go!'
    Then User should not see "hello_world.txt" in the search results
    When User click on "eicar.com"
    Then The page title should be "IRMA | Results"
    When User go back
    Then User should see 'eicar.com' in the search results
    And User should not see 'hello_world.txt' in the search results

  Scenario: As a user, When I enter a search URL, and should be able to see
  the rights results
    Then User should see 'eicar.com' in the search results
    And User should not see 'hello_world.txt' in the search results
