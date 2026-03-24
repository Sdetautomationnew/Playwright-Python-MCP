import time

from pytest_bdd import given, parsers, then, when


def _valid_checkout_info(checkout_provider):
    info = next((item for item in checkout_provider.load_checkout_info() if item["expected_success"]), None)
    assert info, "No valid checkout info found"
    return info


def _error_text(page):
    selectors = (
        "[data-test='error']",
        ".error-message-container h3",
        ".error-message-container",
        ".checkout_info .error-message-container",
        "h3",
    )
    for selector in selectors:
        locator = page.locator(selector)
        if locator.count():
            text = locator.first.text_content() or ""
            if text.strip():
                return text.strip()
    return ""


@given("I log in with valid credentials")
@when("I log in with valid credentials")
def login_with_valid_credentials(login_page, user_provider):
    """Log in with the standard user."""
    login_page.navigate_to(login_page.config.base_url)
    user = next((candidate for candidate in user_provider.load_users() if candidate["username"] == "standard_user"), None)
    assert user, "Standard user not found"
    login_page.login(user["username"], user["password"])


@given(parsers.parse('I log in as "{username}"'))
@when(parsers.parse('I log in as "{username}"'))
def login_as_specific_user(login_page, user_provider, username):
    """Log in as the requested user."""
    login_page.navigate_to(login_page.config.base_url)
    user = next((candidate for candidate in user_provider.load_users() if candidate["username"] == username), None)
    assert user, f"User {username} not found"
    login_page.login(user["username"], user["password"])


@when("I add multiple products to cart")
def add_multiple_products(inventory_page):
    """Add multiple products to the cart."""
    inventory_page.add_product_to_cart("Sauce Labs Backpack")
    inventory_page.add_product_to_cart("Sauce Labs Bike Light")


@when("I proceed to checkout with valid information")
def proceed_with_valid_info(page, checkout_provider):
    """Complete the full checkout flow using valid information."""
    page.locator(".shopping_cart_link").click()
    page.wait_for_url(lambda url: "cart" in url, timeout=5000)
    page.locator("[data-test='checkout']").click()
    page.wait_for_url(lambda url: "checkout-step-one" in url, timeout=5000)

    valid_info = _valid_checkout_info(checkout_provider)
    page.locator("#first-name").fill(valid_info["first_name"])
    page.locator("#last-name").fill(valid_info["last_name"])
    page.locator("#postal-code").fill(valid_info["zip_code"])
    page.locator("[data-test='continue']").click()
    page.wait_for_url(lambda url: "checkout-step-two" in url, timeout=5000)
    page.locator("[data-test='finish']").click()


@when("I complete checkout despite delays")
def complete_checkout_with_delays(page, checkout_provider):
    """Complete checkout for the performance user flow."""
    page.locator(".shopping_cart_link").click()
    page.wait_for_url(lambda url: "cart" in url, timeout=5000)
    page.locator("[data-test='checkout']").click()
    page.wait_for_url(lambda url: "checkout-step-one" in url, timeout=5000)

    time.sleep(3)
    valid_info = _valid_checkout_info(checkout_provider)
    page.locator("#first-name").fill(valid_info["first_name"])
    page.locator("#last-name").fill(valid_info["last_name"])
    page.locator("#postal-code").fill(valid_info["zip_code"])
    page.locator("[data-test='continue']").click()
    page.wait_for_url(lambda url: "checkout-step-two" in url, timeout=5000)
    page.locator("[data-test='finish']").click()


@then(parsers.parse('I should see an error message "{message}"'))
def verify_error_message(page, message):
    """Verify the UI shows the expected error message."""
    actual = _error_text(page)
    assert message in actual, f"Expected error message: {message}, got: {actual}"


@then("I should complete the purchase successfully")
def verify_successful_purchase(checkout_page):
    """Verify the purchase completed."""
    assert checkout_page.is_checkout_complete()


@then("receive order confirmation")
@then("I should see order confirmation")
def verify_order_received(checkout_page):
    """Verify an order confirmation is shown."""
    message = checkout_page.get_completion_message()
    assert "Thank you for your order" in message
