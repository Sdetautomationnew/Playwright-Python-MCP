Feature: Inventory and Product Sorting
  As a Sauce Demo user
  I want to view and sort products
  So that I can find items easily

  @smoke
  Scenario: View all products on inventory page
    Given I am logged in as "standard_user"
    When I am on the inventory page
    Then I should see 6 products displayed
    And each product should have a name and price

  @regression
  Scenario Outline: Sort products by different criteria
    Given I am logged in as "standard_user"
    When I sort products by "<sort_option>"
    Then products should be sorted "<expected_order>"

    Examples:
      | sort_option | expected_order |
      | az          | alphabetically ascending |
      | za          | alphabetically descending |
      | lohi        | price low to high |
      | hilo        | price high to low |

  @edge
  Scenario: Performance glitch user experiences delays
    Given I am logged in as "performance_glitch_user"
    When I am on the inventory page
    Then I should eventually see all products despite delays
