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
 Scenario: Sort products alphabetically from A to Z
 Given I am logged in as "standard_user"
 When I sort products by "az"
 Then products should be sorted "alphabetically ascending"

 @regression
 Scenario: Sort products alphabetically from Z to A
 Given I am logged in as "standard_user"
 When I sort products by "za"
 Then products should be sorted "alphabetically descending"

 @regression
 Scenario: Sort products by price from low to high
 Given I am logged in as "standard_user"
 When I sort products by "lohi"
 Then products should be sorted "price low to high"

 @regression
 Scenario: Sort products by price from high to low
 Given I am logged in as "standard_user"
 When I sort products by "hilo"
 Then products should be sorted "price high to low"

 @regression
 Scenario: Open a product details page from inventory
 Given I am logged in as "standard_user"
 When I open the details page for "Sauce Labs Backpack"
 Then I should be on the product details page
 And the product details should show name "Sauce Labs Backpack"
 And the product details should show a price
 And the product details should show an add to cart button

 @regression
 Scenario: Add every displayed product to the cart
 Given I am logged in as "standard_user"
 When I add every displayed product to the cart
 Then the cart badge should match the number of displayed products

 @edge
 Scenario: Performance glitch user experiences delays
 Given I am logged in as "performance_glitch_user"
 When I am on the inventory page
 Then I should eventually see all products despite delays
