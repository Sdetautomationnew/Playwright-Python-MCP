Feature: Checkout Process
 As a Sauce Demo user
 I want to complete the checkout process
 So that I can purchase my selected items

 @regression
 Scenario: Proceed to checkout from the cart
 Given I am logged in as "standard_user"
 And I have added "Sauce Labs Backpack" to the cart
 When I proceed to checkout
 Then I should be on the checkout information page

 @regression
 Scenario: Checkout information form is visible
 Given I am logged in as "standard_user"
 And I have added "Sauce Labs Backpack" to the cart
 When I proceed to checkout
 Then I should be on the checkout information page
 And I should see the checkout information form

 @regression
 Scenario: Continue from checkout information to checkout overview
 Given I am logged in as "standard_user"
 And I have added "Sauce Labs Backpack" to the cart
 When I proceed to checkout
 And I enter valid checkout information
 And I try to continue
 Then I should be on the checkout overview page

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
 Scenario: Checkout requires a first name
 Given I am logged in as "standard_user"
 And I have added "Sauce Labs Backpack" to the cart
 When I proceed to checkout
 And I leave the first name blank
 And I try to continue
 Then I should see an error message "Error: First Name is required"

 @negative
 Scenario: Checkout requires a last name
 Given I am logged in as "standard_user"
 And I have added "Sauce Labs Backpack" to the cart
 When I proceed to checkout
 And I leave the last name blank
 And I try to continue
 Then I should see an error message "Error: Last Name is required"

 @negative
 Scenario: Checkout requires a zip code
 Given I am logged in as "standard_user"
 And I have added "Sauce Labs Backpack" to the cart
 When I proceed to checkout
 And I leave the zip code blank
 And I try to continue
 Then I should see an error message "Error: Postal Code is required"

 @edge
 Scenario: Checkout with long customer names
 Given I am logged in as "standard_user"
 And I have added "Sauce Labs Backpack" to the cart
 When I proceed to checkout
 And I enter "Alexandria" as first name and "MontgomerySmith" as last name
 And I enter "12345" as zip code
 And I complete the purchase
 Then I should see the order confirmation message
