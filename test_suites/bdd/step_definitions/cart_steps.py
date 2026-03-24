from pytest_bdd import parsers, then, when
from playwright.sync_api import expect


def _remember_product(page, product_name):
    setattr(page, "_last_product_name", product_name)


def _product_locator(page, product_name):
    return page.locator(".inventory_item").filter(has_text=product_name)


@when(parsers.parse('I add "{product_name}" to the cart'))
@when(parsers.parse('I add "{product_name}" to cart'))
def add_product_to_cart(inventory_page, cart_widget, product_name):
    """Add a specific product to the cart."""
    inventory_page.add_product_to_cart(product_name)
    _remember_product(inventory_page.page, product_name)
    assert cart_widget.get_item_count() > 0


@when(parsers.parse('I remove "{product_name}" from the cart'))
def remove_product_from_cart(inventory_page, product_name):
    """Remove a specific product from the cart."""
    inventory_page.remove_product_from_cart(product_name)
    _remember_product(inventory_page.page, product_name)


@when("I navigate to cart page")
def navigate_to_cart(cart_widget):
    """Navigate to the cart page."""
    cart_widget.go_to_cart()


@then(parsers.parse('the cart badge should show "{count}"'))
def verify_cart_badge(cart_widget, count):
    """Verify cart badge count."""
    assert str(cart_widget.get_item_count()) == count


@then("the product should be marked as added")
def verify_product_added(page):
    """Verify the last product switched to its Remove state."""
    product_name = getattr(page, "_last_product_name", "")
    product_locator = _product_locator(page, product_name)
    expect(product_locator.locator("button:has-text('Remove')")).to_be_visible()


@then("the product should be available for adding again")
def verify_product_available(page):
    """Verify the last product can be added to the cart again."""
    product_name = getattr(page, "_last_product_name", "")
    product_locator = _product_locator(page, product_name)
    expect(product_locator.locator("button:has-text('Add to cart')")).to_be_visible()


@then(parsers.parse('I should see "{product_name}" in the cart'))
def verify_product_in_cart(page, cart_widget, product_name):
    """Verify the product is listed in the cart."""
    if "cart" not in page.url:
        cart_widget.go_to_cart()
        page.wait_for_url(lambda url: "cart" in url, timeout=5000)

    cart_items = page.locator(".cart_item .inventory_item_name").all_text_contents()
    assert product_name in cart_items


@then("the cart should contain 1 item")
def verify_cart_item_count(cart_page):
    """Verify cart has one item."""
    assert cart_page.get_cart_item_count() == 1
