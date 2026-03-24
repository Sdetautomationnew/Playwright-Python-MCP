Feature: Checkout Process
  As a Sauce Demo user
  I want to complete the checkout process
  So that I can purchase my selected items

  @e2e
  Scenario: Complete purchase with valid information
    Given I am logged in as "standard_user"
    And I have added "Sauce Labs Backpack" to the cart
    When I proceed to checkout
    And I enter valid checkout information
    And I complete the purchase
    Then I should see the order confirmation message
    And the cart should be empty

  @negative
  Scenario Outline: Checkout with invalid information
    Given I am logged in as "standard_user"
    And I have added "Sauce Labs Backpack" to the cart
    When I proceed to checkout
    And I enter "<field>" as "<value>"
    And I try to continue
    Then I should see an error message "<error_message>"

    Examples:
      | field      | value | error_message |
      | first_name |       | Error: First Name is required |
      | last_name  |       | Error: Last Name is required |
      | zip_code   |       | Error: Postal Code is required |

  @edge
  Scenario: Checkout with long customer names
    Given I am logged in as "standard_user"
    And I have added "Sauce Labs Backpack" to the cart
    When I proceed to checkout
    And I enter "Alexandria" as first name and "MontgomerySmith" as last name
    And I enter "12345" as zip code
    And I complete the purchase
    Then I should see the order confirmation message
