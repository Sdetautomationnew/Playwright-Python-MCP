Feature: Fake Store API Endpoints Testing
  As an API consumer
  I want to test public API endpoints using Fake Store API
  So that I can verify API functionality

  @api @smoke
  Scenario: Get all products from store
    When I send a GET request to "/products"
    Then the response status code should be 200
    And the response should contain a list of products
    And each product should have required fields: "id", "title", "price"

  @api @smoke
  Scenario: Get product by specific ID
    When I send a GET request to "/products/1"
    Then the response status code should be 200
    And the response should contain product title
    And the response should contain price information

  @api @regression
  Scenario: Get product with invalid ID returns empty response
    When I send a GET request to "/products/999999"
    Then the response status code should be 200
    And the response should be empty or not contain product

  @api @smoke
  Scenario: Get all product categories
    When I send a GET request to "/products/categories"
    Then the response status code should be 200
    And the response should contain list of categories

  @api @regression
  Scenario: Get products in specific category
    When I send a GET request to "/products/category/electronics"
    Then the response status code should be 200
    And the response should contain only electronics products

  @api @smoke
  Scenario: Get all users from store
    When I send a GET request to "/users"
    Then the response status code should be 200
    And the response should contain user list

  @api @regression
  Scenario: Get specific user by ID
    When I send a GET request to "/users/1"
    Then the response status code should be 200
    And the response should contain user information

  @api @smoke
  Scenario: Get all carts
    When I send a GET request to "/carts"
    Then the response status code should be 200
    And the response should contain list of carts

  @api @regression
  Scenario: Get specific cart by ID
    When I send a GET request to "/carts/1"
    Then the response status code should be 200
    And the response should contain cart items

  @api @smoke
  Scenario: Get user cart
    When I send a GET request to "/carts/user/1"
    Then the response status code should be 200
    And the response should contain user cart data

  @api @edge
  Scenario: Add new product to store
    When I send a POST request to "/products" with data:
      | title       | Test Product  |
      | price       | 99.99         |
      | description | A test product |
      | image       | http://test.jpg |
      | category    | test          |
    Then the response status code should be 201

  @api @edge
  Scenario: Create new cart
    When I send a POST request to "/carts" with data:
      | userId | 1 |
      | date   | 2024-01-01 |
      | products | [{"productId":1,"quantity":5}] |
    Then the response status code should be 201

  @api @regression
  Scenario: Update cart by ID
    When I send a PUT request to "/carts/1" with data:
      | userId | 1 |
      | date   | 2024-01-01 |
      | products | [{"productId":1,"quantity":3}] |
    Then the response status code should be 200

  @api @regression
  Scenario: Delete cart by ID
    When I send a DELETE request to "/carts/1"
    Then the response status code should be 200

  @api @smoke
  Scenario: Get limited products
    When I send a GET request to "/products?limit=5"
    Then the response status code should be 200
    And the response should contain maximum 5 products

  @api @regression
  Scenario: Sort products ascending by price
    When I send a GET request to "/products?sort=asc"
    Then the response status code should be 200
    And the response should contain sorted products list
