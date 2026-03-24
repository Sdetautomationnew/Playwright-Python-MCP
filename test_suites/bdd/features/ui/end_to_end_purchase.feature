Feature: End-to-End Purchase
  As a Sauce Demo user
  I want to complete a full purchase journey
  So that I can buy products from start to finish

  @e2e
  Scenario: Complete purchase journey
    Given I am on the login page
    When I log in with valid credentials
    And I add multiple products to cart
    And I proceed to checkout with valid information
    Then I should complete the purchase successfully
    And receive order confirmation

  @performance
  Scenario: Performance glitch user complete journey
    Given I am on the login page
    When I log in as "performance_glitch_user"
    And I add "Sauce Labs Backpack" to cart
    And I complete checkout despite delays
    Then I should see order confirmation

  @mcp
  Scenario: MCP-assisted purchase journey
    Given MCP integration is enabled
    When I perform login via MCP
    And I add products via MCP
    And I complete checkout via MCP
    Then the purchase should succeed with MCP assistance
