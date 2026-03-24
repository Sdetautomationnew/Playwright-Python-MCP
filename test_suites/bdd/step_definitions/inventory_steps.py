import time

from pytest_bdd import given, parsers, then, when
from playwright.sync_api import expect


@given("I am on the inventory page")
@when("I am on the inventory page")
def verify_on_inventory_page(inventory_page):
    """Verify the inventory page is visible."""
    expect(inventory_page.page.locator(".inventory_list")).to_be_visible()


@when(parsers.parse('I sort products by "{sort_option}"'))
def sort_products(inventory_page, sort_option):
    """Sort products by the requested option."""
    inventory_page.sort_products(sort_option)


@then(parsers.parse("I should see {count:d} products displayed"))
def verify_product_count(inventory_page, count):
    """Verify number of products displayed."""
    assert inventory_page.get_product_count() == count


@then("each product should have a name and price")
def verify_product_details(inventory_page):
    """Verify each product has a name and price."""
    products = inventory_page.get_product_names()
    assert products, "Expected at least one inventory item"
    for product in products:
        assert product.strip(), "Product name should not be empty"

    prices = inventory_page.page.locator(".inventory_item_price").all_text_contents()
    assert prices, "Expected price labels for inventory items"
    for price in prices:
        assert price.strip().startswith("$"), f"Unexpected price label: {price}"


@then(parsers.parse('products should be sorted "{order}"'))
def verify_sorting(inventory_page, order):
    """Verify products are sorted correctly."""
    if "alphabetically" in order:
        products = inventory_page.get_product_names()
        expected = sorted(products, reverse="descending" in order)
        assert products == expected
        return

    prices = [
        float(price.strip().replace("$", ""))
        for price in inventory_page.page.locator(".inventory_item_price").all_text_contents()
    ]
    expected = sorted(prices, reverse="high to low" in order)
    assert prices == expected


@then("I should eventually see all products despite delays")
def verify_products_with_delay(inventory_page):
    """Verify products load despite performance issues."""
    time.sleep(2)
    assert inventory_page.get_product_count() == 6
