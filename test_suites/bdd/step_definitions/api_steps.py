import pytest
from pytest_bdd import given, parsers, then, when

from app.api.clients.sauce_demo_api_client import SauceDemoAPIClient
from core.reporting.telemetry_client import get_logger

logger = get_logger(__name__)


def _try_parse_json(response):
    """
    Safely parse JSON responses.

    Fake Store API (or network egress) may return HTML (e.g. 403 "Just a moment...")
    which would crash step execution if we call `response.json()` unconditionally.
    """
    if not getattr(response, "content", None):
        return None
    try:
        return response.json()
    except Exception:
        return None


@pytest.fixture(scope="session")
def api_client(env_config):
    """Provide the API client for Sauce Demo API scenarios."""
    if not env_config.api_url:
        pytest.skip("API_URL is not configured for Sauce Demo API BDD scenarios.")
    client = SauceDemoAPIClient(env_config)

    # Probe once: on some CI runners outbound requests to fakestoreapi.com return 403 HTML.
    # In that case, skip API BDD scenarios rather than failing due to JSON decoding errors.
    try:
        probe = client.get("/products")
        if probe.status_code != 200:
            pytest.skip(f"Fake Store API not accessible (status {probe.status_code}).")
    except Exception as exc:
        pytest.skip(f"Fake Store API not accessible: {exc}")

    return client


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
    api_response["data"] = _try_parse_json(response)
    api_response["response"] = response
    logger.info(f"GET {endpoint} - Status: {response.status_code}")


@when(parsers.parse('I send a POST request to "{endpoint}" with credentials:'))
def when_send_post_with_credentials(api_client, api_response, endpoint, datatable):
    """Send a POST request with credential data."""
    headers, values = datatable[0], datatable[1]
    credentials = dict(zip(headers, values))
    response = api_client.post(endpoint, json=credentials)
    api_response["status_code"] = response.status_code
    api_response["data"] = _try_parse_json(response)
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
    api_response["data"] = _try_parse_json(response)
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
    api_response["data"] = _try_parse_json(response)
    api_response["response"] = response
    logger.info(f"PUT {endpoint} - Status: {response.status_code}")


@when(parsers.parse('I send a DELETE request to "{endpoint}"'))
def when_send_delete_request(api_client, api_response, endpoint):
    """Send a DELETE request to the endpoint."""
    response = api_client.delete(endpoint)
    api_response["status_code"] = response.status_code
    api_response["data"] = _try_parse_json(response)
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


@then("the response should contain product title")
def then_response_has_product_title(api_response):
    """Verify product response has a title field."""
    data = api_response["data"]
    assert "title" in data, "Product response missing 'title' field"


@then("the response should contain list of categories")
def then_response_has_categories(api_response):
    """Verify response contains a list of categories."""
    data = api_response["data"]
    assert isinstance(data, list), "Categories response should be a list"
    assert len(data) > 0, "Categories list should not be empty"


@then("the response should contain only electronics products")
def then_response_has_electronics(api_response):
    """Verify response contains only electronics products."""
    products = api_response["data"]
    assert isinstance(products, list), "Response should be a list"
    assert len(products) > 0, "Electronics list should not be empty"
    for product in products:
        assert product.get("category") == "electronics", f"Non-electronics product found: {product}"


@then("the response should contain user list")
def then_response_has_users(api_response):
    """Verify response contains a list of users."""
    data = api_response["data"]
    assert isinstance(data, list), "Users response should be a list"
    assert len(data) > 0, "Users list should not be empty"
    # Check that users have expected fields
    if data:
        assert "id" in data[0], "User should have 'id' field"


@then("the response should contain user information")
def then_response_has_user_info(api_response):
    """Verify response contains user information."""
    data = api_response["data"]
    assert isinstance(data, dict), "User response should be a dict"
    assert "id" in data, "User should have 'id' field"


@then("the response should contain list of carts")
def then_response_has_carts(api_response):
    """Verify response contains a list of carts."""
    data = api_response["data"]
    assert isinstance(data, list), "Carts response should be a list"
    assert len(data) > 0, "Carts list should not be empty"


@then("the response should contain cart items")
def then_response_has_cart_content(api_response):
    """Verify response contains cart items."""
    data = api_response["data"]
    assert isinstance(data, dict), "Cart response should be a dict"
    # Fake Store API's cart structure
    products = data.get("products", [])
    assert isinstance(products, list), "Cart products should be a list"


@then("the response should contain user cart data")
def then_response_has_user_cart(api_response):
    """Verify response contains user cart data."""
    data = api_response["data"]
    if isinstance(data, dict):
        assert "products" in data or "items" in data, "Cart data should have products or items"
    elif isinstance(data, list):
        # Might be a list of carts
        assert len(data) > 0, "Cart list should not be empty"


@then("the response should contain maximum 5 products")
def then_response_has_max_5_products(api_response):
    """Verify response contains at most 5 products."""
    data = api_response["data"]
    assert isinstance(data, list), "Response should be a list"
    assert len(data) <= 5, f"Expected at most 5 products, got {len(data)}"
    assert len(data) > 0, "Response should not be empty"


@then("the response should contain sorted products list")
def then_response_has_sorted_list(api_response):
    """Verify response contains a sorted products list."""
    data = api_response["data"]
    assert isinstance(data, list), "Response should be a list"
    assert len(data) > 0, "Products list should not be empty"


@then("the response should be empty or not contain product")
def then_response_is_empty_or_invalid(api_response):
    """Verify response is empty for invalid product ID."""
    data = api_response["data"]
    # For Fake Store API, invalid IDs return empty dict or null
    assert not data or len(str(data)) == 2, "Invalid ID should return empty/null response"
