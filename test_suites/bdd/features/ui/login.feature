Feature: User Authentication
  As a Sauce Demo user
  I want to log in to the application
  So that I can access the inventory

  @smoke
  Scenario Outline: Successful login with valid credentials
    Given I am on the login page
    When I enter username "<username>" and password "<password>"
    And I click the login button
    Then I should be redirected to the inventory page
    And I should see products displayed

    Examples:
      | username      | password     |
      | standard_user | secret_sauce |

  @negative
  Scenario Outline: Failed login with invalid credentials
    Given I am on the login page
    When I enter username "<username>" and password "<password>"
    And I click the login button
    Then I should see an error message "<error_message>"
    And I should remain on the login page

    Examples:
      | username      | password     | error_message |
      | invalid_user  | wrong_pass   | Epic sadface: Username and password do not match any user in this service |

  @edge
  Scenario: Login with locked out user
    Given I am on the login page
    When I enter username "locked_out_user" and password "secret_sauce"
    And I click the login button
    Then I should see an error message "Epic sadface: Sorry, this user has been locked out."
    And I should remain on the login page
