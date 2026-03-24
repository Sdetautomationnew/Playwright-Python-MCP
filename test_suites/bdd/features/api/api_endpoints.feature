Feature: Sauce Demo API Endpoints
  As an API consumer
  I want to test Sauce Demo API endpoints
  So that I can verify correct API functionality

  @api @smoke
  Scenario: Get all products from inventory
    When I send a GET request to "/api/v1/products"
    Then the response status code should be 200
    And the response should contain a list of products
    And each product should have required fields: "id", "name", "price"

  @api @smoke
  Scenario: Get product by specific ID
    When I send a GET request to "/api/v1/products/1"
    Then the response status code should be 200
    And the response should have product name "Sauce Labs Backpack"
    And the response should contain price information

  @api @regression
  Scenario: Get product with invalid ID returns 404
    When I send a GET request to "/api/v1/products/999999"
    Then the response status code should be 404
    And the response should contain error message

  @api @smoke
  Scenario: User login with valid credentials
    When I send a POST request to "/api/v1/auth/login" with credentials:
      | username      | standard_user |
      | password      | secret_sauce  |
    Then the response status code should be 200
    And the response should contain a valid session token

  @api @negative
  Scenario: User login with invalid credentials
    When I send a POST request to "/api/v1/auth/login" with credentials:
      | username | invalid_user   |
      | password | wrong_password |
    Then the response status code should be 401
    And the response should contain error message "Invalid credentials"

  @api @regression
  Scenario: User login with locked out account
    When I send a POST request to "/api/v1/auth/login" with credentials:
      | username | locked_out_user |
      | password | secret_sauce    |
    Then the response status code should be 401
    And the response should contain error message "User is locked out"

  @api @smoke
  Scenario: Add product to cart
    Given I have a valid session token for "standard_user"
    When I send a POST request to "/api/v1/cart/add" with data:
      | product_id | 1      |
      | quantity   | 2      |
    Then the response status code should be 200
    And the response should confirm product added
    And the response should show cart count as 2

  @api @regression
  Scenario: Remove product from cart
    Given I have a valid session token for "standard_user"
    And I have added product with ID "1" to cart
    When I send a DELETE request to "/api/v1/cart/items/1"
    Then the response status code should be 200
    And the response should confirm product removed
    And the response should show updated cart

  @api @regression
  Scenario: Get cart contents
    Given I have a valid session token for "standard_user"
    And I have added products to cart
    When I send a GET request to "/api/v1/cart"
    Then the response status code should be 200
    And the response should contain all cart items
    And the response should have total price calculation

  @api @regression
  Scenario: Update product quantity in cart
    Given I have a valid session token for "standard_user"
    And I have added product with ID "1" to cart
    When I send a PUT request to "/api/v1/cart/items/1" with data:
      | quantity | 5 |
    Then the response status code should be 200
    And the response should confirm quantity updated to 5
    And the response should recalculate total price

  @api @regression
  Scenario: Get product filters and sorting options
    When I send a GET request to "/api/v1/products/filters"
    Then the response status code should be 200
    And the response should contain available filters
    And the response should contain sorting options

  @api @regression
  Scenario: Sort products by price
    When I send a GET request to "/api/v1/products?sort=price&order=asc"
    Then the response status code should be 200
    And the response should contain sorted products list
    And the first product should have lowest price

  @api @regression
  Scenario: Filter products by category
    When I send a GET request to "/api/v1/products?category=shirts"
    Then the response status code should be 200
    And the response should contain only shirt products
    And each product should have category "shirts"

  @api @edge
  Scenario: Checkout with valid cart
    Given I have a valid session token for "standard_user"
    And I have a non-empty cart with items
    When I send a POST request to "/api/v1/checkout" with data:
      | first_name | John      |
      | last_name  | Doe       |
      | zip_code   | 12345     |
    Then the response status code should be 200
    And the response should contain order confirmation

  @api @negative
  Scenario: Checkout with missing required fields
    Given I have a valid session token for "standard_user"
    When I send a POST request to "/api/v1/checkout" with data:
      | first_name |           |
      | last_name  | Doe       |
      | zip_code   | 12345     |
    Then the response status code should be 400
    And the response should contain validation error for "first_name"

  @api @regression
  Scenario: Get checkout summary before payment
    Given I have a valid session token for "standard_user"
    And I have a non-empty cart
    When I send a GET request to "/api/v1/checkout/summary"
    Then the response status code should be 200
    And the response should contain items breakdown
    And the response should contain total price calculation
    And the response should contain tax information

  @api @smoke
  Scenario: User logout
    Given I have a valid session token for "standard_user"
    When I send a POST request to "/api/v1/auth/logout"
    Then the response status code should be 200
    And the response should confirm successful logout
