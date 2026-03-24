from pytest_bdd import given, then, when


@given("MCP integration is enabled")
def verify_mcp_enabled(mcp_client):
    """Verify MCP integration is enabled."""
    assert mcp_client.connected, "MCP integration not enabled"


@when("I perform login via MCP")
def login_via_mcp(login_page, mcp_client, user_provider):
    """Perform login using MCP with a Playwright fallback."""

    def mcp_login():
        login_page.navigate_to(login_page.config.base_url)
        user = next((candidate for candidate in user_provider.load_users() if candidate["username"] == "standard_user"), None)
        assert user, "Standard user not found"
        mcp_client.mcp_fill(login_page.page, "#user-name", user["username"])
        mcp_client.mcp_fill(login_page.page, "#password", user["password"])
        mcp_client.mcp_click(login_page.page, "#login-button")
        return True

    def pom_login():
        login_page.navigate_to(login_page.config.base_url)
        user = next((candidate for candidate in user_provider.load_users() if candidate["username"] == "standard_user"), None)
        assert user, "Standard user not found"
        login_page.login(user["username"], user["password"])
        return True

    mcp_client.execute_with_fallback(mcp_login, pom_login, "login")


@when("I add products via MCP")
def add_products_via_mcp(inventory_page, mcp_client):
    """Add products using MCP."""

    def mcp_add():
        mcp_client.mcp_click(inventory_page.page, "[data-test='add-to-cart-sauce-labs-backpack']")
        return True

    def pom_add():
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        return True

    mcp_client.execute_with_fallback(mcp_add, pom_add, "add_product")


@when("I complete checkout via MCP")
def complete_checkout_via_mcp(cart_page, checkout_page, mcp_client, checkout_provider):
    """Complete checkout using MCP."""

    def mcp_checkout():
        if "cart" not in cart_page.page.url:
            cart_page.page.locator(".shopping_cart_link").click()
            cart_page.page.wait_for_url(lambda url: "cart" in url, timeout=5000)
        mcp_client.mcp_click(cart_page.page, "[data-test='checkout']")
        valid_info = next((info for info in checkout_provider.load_checkout_info() if info["expected_success"]), None)
        assert valid_info, "No valid checkout info found"
        mcp_client.mcp_fill(checkout_page.page, "[data-test='firstName']", valid_info["first_name"])
        mcp_client.mcp_fill(checkout_page.page, "[data-test='lastName']", valid_info["last_name"])
        mcp_client.mcp_fill(checkout_page.page, "[data-test='postalCode']", valid_info["zip_code"])
        mcp_client.mcp_click(checkout_page.page, "[data-test='continue']")
        checkout_page.page.wait_for_url(lambda url: "checkout-step-two" in url, timeout=5000)
        mcp_client.mcp_click(checkout_page.page, "[data-test='finish']")
        return True

    def pom_checkout():
        if "cart" not in cart_page.page.url:
            cart_page.page.locator(".shopping_cart_link").click()
            cart_page.page.wait_for_url(lambda url: "cart" in url, timeout=5000)
        cart_page.proceed_to_checkout()
        valid_info = next((info for info in checkout_provider.load_checkout_info() if info["expected_success"]), None)
        assert valid_info, "No valid checkout info found"
        checkout_page.fill_checkout_information(
            valid_info["first_name"],
            valid_info["last_name"],
            valid_info["zip_code"],
        )
        checkout_page.continue_checkout()
        checkout_page.finish_checkout()
        return True

    mcp_client.execute_with_fallback(mcp_checkout, pom_checkout, "checkout")


@then("the purchase should succeed with MCP assistance")
def verify_mcp_purchase(checkout_page):
    """Verify purchase succeeded with MCP."""
    assert checkout_page.is_checkout_complete()
