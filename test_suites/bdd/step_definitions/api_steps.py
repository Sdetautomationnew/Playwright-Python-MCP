import pytest
from pytest_bdd import given, parsers, then, when

from app.api.clients.sauce_demo_api_client import SauceDemoAPIClient
from core.reporting.telemetry_client import get_logger

logger = get_logger(__name__)


@pytest.fixture
def api_client(env_config):
    """Provide the API client for Sauce Demo API scenarios."""
    if not env_config.api_url:
        pytest.skip("API_URL is not configured for Sauce Demo API BDD scenarios.")
    return SauceDemoAPIClient(env_config)


@pytest.fixture
def api_response():
    """Store the latest API response details."""
    return {}


@pytest.fixture
def cart_items():
    """Store cart items added during a scenario."""
    return []


@given(parsers.parse('I have a valid session token for "{username}"'))
def given_valid_session_token(api_client, username):
    """Authenticate and persist the token on the API client."""
    response = api_client.login(username, "secret_sauce")
    assert response.status_code == 200, f"Login failed: {response.text}"


@given(parsers.parse('I have added product with ID "{product_id}" to cart'))
def given_product_added_to_cart(api_client, product_id, cart_items):
    """Add a product to the cart."""
    response = api_client.add_to_cart(int(product_id), 1)
    assert response.status_code == 200, f"Add to cart failed: {response.text}"
    cart_items.append({"product_id": int(product_id), "quantity": 1})


@given("I have added products to cart")
def given_products_added_to_cart(api_client, cart_items):
    """Add multiple products to cart for testing."""
    products = (
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 1},
    )
    for product in products:
        response = api_client.add_to_cart(product["product_id"], product["quantity"])
        assert response.status_code == 200, f"Add to cart failed: {response.text}"
        cart_items.append(product)


@given("I have a non-empty cart with items")
@given("I have a non-empty cart")
def given_non_empty_cart(api_client):
    """Ensure the cart has at least one item."""
    response = api_client.add_to_cart(1, 1)
    assert response.status_code == 200, f"Add to cart failed: {response.text}"


@when(parsers.parse('I send a GET request to "{endpoint}"'))
def when_send_get_request(api_client, api_response, endpoint):
    """Send a GET request to the endpoint."""
    response = api_client.get(endpoint)
    api_response["status_code"] = response.status_code
    api_response["data"] = response.json() if response.content else None
    api_response["response"] = response
    logger.info(f"GET {endpoint} - Status: {response.status_code}")


@when(parsers.parse('I send a POST request to "{endpoint}" with credentials:'))
def when_send_post_with_credentials(api_client, api_response, endpoint, datatable):
    """Send a POST request with credential data."""
    headers, values = datatable[0], datatable[1]
    credentials = dict(zip(headers, values))
    response = api_client.post(endpoint, json=credentials)
    api_response["status_code"] = response.status_code
    api_response["data"] = response.json() if response.content else None
    api_response["response"] = response
    logger.info(f"POST {endpoint} - Status: {response.status_code}")


@when(parsers.parse('I send a POST request to "{endpoint}" with data:'))
def when_send_post_with_data(api_client, api_response, endpoint, datatable):
    """Send a POST request with payload data."""
    headers, values = datatable[0], datatable[1]
    data = {
        key: int(value) if value and value.isdigit() else value
        for key, value in zip(headers, values)
    }
    response = api_client.post(endpoint, json=data)
    api_response["status_code"] = response.status_code
    api_response["data"] = response.json() if response.content else None
    api_response["response"] = response
    logger.info(f"POST {endpoint} - Status: {response.status_code}")


@when(parsers.parse('I send a PUT request to "{endpoint}" with data:'))
def when_send_put_with_data(api_client, api_response, endpoint, datatable):
    """Send a PUT request with payload data."""
    headers, values = datatable[0], datatable[1]
    data = {
        key: int(value) if value and value.isdigit() else value
        for key, value in zip(headers, values)
    }
    response = api_client.put(endpoint, json=data)
    api_response["status_code"] = response.status_code
    api_response["data"] = response.json() if response.content else None
    api_response["response"] = response
    logger.info(f"PUT {endpoint} - Status: {response.status_code}")


@when(parsers.parse('I send a DELETE request to "{endpoint}"'))
def when_send_delete_request(api_client, api_response, endpoint):
    """Send a DELETE request to the endpoint."""
    response = api_client.delete(endpoint)
    api_response["status_code"] = response.status_code
    api_response["data"] = response.json() if response.content else None
    api_response["response"] = response
    logger.info(f"DELETE {endpoint} - Status: {response.status_code}")


@then(parsers.parse("the response status code should be {status_code:d}"))
def then_check_status_code(api_response, status_code):
    """Verify response status code."""
    assert api_response["status_code"] == status_code


@then("the response should contain a list of products")
def then_response_contains_products(api_response):
    """Verify response contains a products list."""
    data = api_response["data"]
    assert isinstance(data, list)
    assert data


@then(parsers.parse("each product should have required fields: {fields}"))
def then_products_have_required_fields(api_response, fields):
    """Verify each product contains the requested fields."""
    required_fields = [field.strip().strip('"') for field in fields.split(",")]
    for product in api_response["data"]:
        for field in required_fields:
            assert field in product, f"Product missing field: {field}"


@then("the response should contain price information")
def then_response_has_price(api_response):
    """Verify price information exists in the response."""
    data = api_response["data"]
    assert "price" in data or "original_price" in data


@then("the response should contain error message")
def then_response_has_error_message(api_response):
    """Verify an error message exists in the response."""
    data = api_response["data"]
    assert "error" in data or "message" in data


@then(parsers.parse('the response should have product name "{product_name}"'))
def then_response_has_product_name(api_response, product_name):
    """Verify the response contains the requested product."""
    data = api_response["data"]
    actual = data.get("name") or data.get("title")
    assert actual == product_name


@then(parsers.parse('the response should contain error message "{error_message}"'))
def then_response_has_specific_error(api_response, error_message):
    """Verify the response contains a specific error message."""
    data = api_response["data"]
    error = data.get("error") or data.get("message", "")
    assert error_message.lower() in error.lower()


@then("the response should contain a valid session token")
def then_response_has_session_token(api_response):
    """Verify the response contains a session token."""
    data = api_response["data"]
    assert data.get("token")


@then("the response should confirm product added")
def then_response_confirms_product_added(api_response):
    """Verify the add-to-cart response looks successful."""
    data = api_response["data"]
    assert "success" in data or "status" in data


@then(parsers.parse("the response should show cart count as {count:d}"))
def then_response_shows_cart_count(api_response, count):
    """Verify the cart count matches the expected quantity."""
    data = api_response["data"]
    actual = data.get("cart_count") or data.get("quantity")
    assert actual == count


@then("the response should confirm product removed")
def then_response_confirms_product_removed(api_response):
    """Verify product removal is acknowledged."""
    data = api_response["data"]
    assert "success" in data or "status" in data or "removed" in data


@then("the response should show updated cart")
def then_response_shows_updated_cart(api_response):
    """Verify the response contains cart data after removal."""
    data = api_response["data"]
    assert "items" in data or "cart" in data


@then("the response should contain all cart items")
def then_response_contains_all_cart_items(api_response):
    """Verify cart items are returned."""
    data = api_response["data"]
    items = data.get("items") or data.get("products")
    assert isinstance(items, list)


@then("the response should have total price calculation")
def then_response_has_total_price(api_response):
    """Verify the response contains total price data."""
    data = api_response["data"]
    assert "total" in data or "total_price" in data


@then(parsers.parse("the response should confirm quantity updated to {quantity:d}"))
def then_response_confirms_quantity_update(api_response, quantity):
    """Verify the updated quantity."""
    data = api_response["data"]
    actual = data.get("quantity") or data.get("new_quantity")
    assert actual == quantity


@then("the response should recalculate total price")
def then_response_recalculates_price(api_response):
    """Verify total price gets recalculated."""
    data = api_response["data"]
    assert "total" in data or "total_price" in data


@then("the response should contain available filters")
def then_response_has_filters(api_response):
    """Verify product filter metadata exists."""
    data = api_response["data"]
    assert "filters" in data or "categories" in data


@then("the response should contain sorting options")
def then_response_has_sorting_options(api_response):
    """Verify sorting metadata exists."""
    data = api_response["data"]
    assert "sort" in data or "sorting" in data


@then("the response should contain sorted products list")
def then_response_has_sorted_products(api_response):
    """Verify a sorted products list is returned."""
    data = api_response["data"]
    assert isinstance(data, list) and data


@then("the first product should have lowest price")
def then_first_product_has_lowest_price(api_response):
    """Verify the first returned product has the lowest price."""
    products = api_response["data"]
    if len(products) > 1:
        first_price = float(products[0].get("price", 0))
        second_price = float(products[1].get("price", 0))
        assert first_price <= second_price


@then("the response should contain only shirt products")
def then_response_has_only_shirts(api_response):
    """Verify only shirt products are returned."""
    for product in api_response["data"]:
        assert "shirt" in product.get("category", "").lower()


@then(parsers.parse('each product should have category "{category}"'))
def then_products_have_category(api_response, category):
    """Verify all products share a category."""
    for product in api_response["data"]:
        assert product.get("category", "").lower() == category.lower()


@then("the response should contain order confirmation")
def then_response_has_order_confirmation(api_response):
    """Verify order confirmation metadata exists."""
    data = api_response["data"]
    assert "order_id" in data or "confirmation" in data


@then(parsers.parse('the response should contain validation error for "{field}"'))
def then_response_has_validation_error(api_response, field):
    """Verify the response reports a validation error."""
    data = api_response["data"]
    errors = data.get("errors", {})
    assert field in errors or field in str(data)


@then("the response should contain items breakdown")
def then_response_has_items_breakdown(api_response):
    """Verify checkout summary contains item breakdown."""
    data = api_response["data"]
    assert "items" in data or "products" in data


@then("the response should contain tax information")
def then_response_has_tax_info(api_response):
    """Verify checkout summary contains tax information."""
    data = api_response["data"]
    assert "tax" in data or "taxes" in data


@then("the response should confirm successful logout")
def then_response_confirms_logout(api_response):
    """Verify logout response looks successful."""
    data = api_response["data"]
    assert "success" in data or "message" in data
