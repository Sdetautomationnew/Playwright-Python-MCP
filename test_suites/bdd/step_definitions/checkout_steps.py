from pytest_bdd import given, parsers, then, when


def _navigate_to_checkout_step_one(page):
    if "checkout-step-one" in page.url:
        return

    if "cart" not in page.url:
        page.locator(".shopping_cart_link").click()
        page.wait_for_url(lambda url: "cart" in url, timeout=5000)

    page.locator("[data-test='checkout']").click()
    page.wait_for_url(lambda url: "checkout-step-one" in url, timeout=5000)


def _valid_checkout_info(checkout_provider):
    info = next((item for item in checkout_provider.load_checkout_info() if item["expected_success"]), None)
    assert info, "No valid checkout info found"
    return info


@given(parsers.parse('I have added "{product_name}" to the cart'))
def add_product_to_cart_setup(inventory_page, product_name):
    """Set up the cart with a product."""
    inventory_page.add_product_to_cart(product_name)


@when("I proceed to checkout")
def proceed_to_checkout(cart_page):
    """Open the checkout information step."""
    _navigate_to_checkout_step_one(cart_page.page)


@when("I enter valid checkout information")
def enter_valid_checkout_info(checkout_page, checkout_provider):
    """Fill the checkout form with valid data."""
    _navigate_to_checkout_step_one(checkout_page.page)
    valid_info = _valid_checkout_info(checkout_provider)
    checkout_page.fill_checkout_information(
        valid_info["first_name"],
        valid_info["last_name"],
        valid_info["zip_code"],
    )


@when(parsers.re(r'^I enter "(?P<field>[^"]+)" as "(?P<value>[^"]*)"$'))
def enter_checkout_field(checkout_page, checkout_provider, field, value):
    """Fill a single checkout field while keeping the other values valid."""
    _navigate_to_checkout_step_one(checkout_page.page)
    valid_info = _valid_checkout_info(checkout_provider)
    form_data = {
        "first_name": valid_info["first_name"],
        "last_name": valid_info["last_name"],
        "zip_code": valid_info["zip_code"],
    }
    form_data[field] = value
    checkout_page.fill_checkout_information(
        form_data["first_name"],
        form_data["last_name"],
        form_data["zip_code"],
    )


@when(parsers.re(r'^I enter "(?P<first_name>[^"]*)" as first name and "(?P<last_name>[^"]*)" as last name$'))
def enter_first_and_last_name(checkout_page, first_name, last_name):
    """Fill the first and last name fields with custom values."""
    _navigate_to_checkout_step_one(checkout_page.page)
    checkout_page.page.locator("#first-name").fill(first_name)
    checkout_page.page.locator("#last-name").fill(last_name)


@when(parsers.re(r'^I enter "(?P<zip_code>[^"]*)" as zip code$'))
def enter_zip_code(checkout_page, zip_code):
    """Fill only the zip code field."""
    _navigate_to_checkout_step_one(checkout_page.page)
    checkout_page.page.locator("#postal-code").fill(zip_code)


@when("I try to continue")
def try_continue_checkout(checkout_page):
    """Attempt to continue checkout."""
    checkout_page.continue_checkout()


@when("I complete the purchase")
def complete_purchase(checkout_page):
    """Continue to the summary page and finish the purchase."""
    if "checkout-step-one" in checkout_page.page.url:
        checkout_page.continue_checkout()
        try:
            checkout_page.page.locator("#finish").wait_for(state="visible", timeout=15000)
        except Exception as exc:
            error_message = checkout_page.checkout_form.get_error_message()
            current_values = {
                "first_name": checkout_page.page.locator("#first-name").input_value(),
                "last_name": checkout_page.page.locator("#last-name").input_value(),
                "zip_code": checkout_page.page.locator("#postal-code").input_value(),
            }
            raise AssertionError(
                "Checkout did not reach the summary page. "
                f"error={error_message!r}, values={current_values!r}"
            ) from exc
    checkout_page.finish_checkout()


@then("I should see the order confirmation message")
def verify_order_confirmation(checkout_page):
    """Verify the checkout confirmation message."""
    assert checkout_page.is_checkout_complete()


@then("the cart should be empty")
def verify_cart_empty(cart_widget):
    """Verify the cart is empty after purchase."""
    assert cart_widget.get_item_count() == 0
