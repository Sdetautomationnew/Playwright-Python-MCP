Feature: Cart Management
  As a Sauce Demo user
  I want to add and remove items from cart
  So that I can purchase selected products

  @smoke
  Scenario: Add single product to cart
    Given I am logged in as "standard_user"
    When I add "Sauce Labs Backpack" to the cart
    Then the cart badge should show "1"
    And the product should be marked as added

  @regression
  Scenario: Add multiple products to cart
    Given I am logged in as "standard_user"
    When I add "Sauce Labs Backpack" to the cart
    And I add "Sauce Labs Bike Light" to the cart
    Then the cart badge should show "2"

  @regression
  Scenario: Remove product from cart
    Given I am logged in as "standard_user"
    When I add "Sauce Labs Backpack" to the cart
    And I remove "Sauce Labs Backpack" from the cart
    Then the cart badge should show "0"
    And the product should be available for adding again

  @edge
  Scenario: Cart persistence across page navigation
    Given I am logged in as "standard_user"
    When I add "Sauce Labs Backpack" to the cart
    And I navigate to cart page
    Then I should see "Sauce Labs Backpack" in the cart
    And the cart should contain 1 item
