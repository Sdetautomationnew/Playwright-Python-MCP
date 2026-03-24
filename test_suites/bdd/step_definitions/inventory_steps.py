import time

from pytest_bdd import given, parsers, then, when
from playwright.sync_api import expect


@given('I am on the inventory page')
@when('I am on the inventory page')
def verify_on_inventory_page(inventory_page):
	expect(inventory_page.page.locator('.inventory_list')).to_be_visible()


@when(parsers.parse('I sort products by "{sort_option}"'))
def sort_products(inventory_page, sort_option):
	inventory_page.sort_products(sort_option)


@when(parsers.parse('I open the details page for "{product_name}"'))
def open_product_details(page, inventory_page, product_name):
	product_card = page.locator('.inventory_item').filter(has_text=product_name)
	inventory_page.tap_or_click(product_card.locator('.inventory_item_name'))


@when('I add every displayed product to the cart')
def add_every_displayed_product_to_cart(page, inventory_page):
	product_names = inventory_page.get_product_names()
	setattr(page, '_displayed_product_count', len(product_names))
	for product_name in product_names:
		inventory_page.add_product_to_cart(product_name)


@then(parsers.parse('I should see {count:d} products displayed'))
def verify_product_count(inventory_page, count):
	assert inventory_page.get_product_count() == count


@then('each product should have a name and price')
def verify_product_details(inventory_page):
	products = inventory_page.get_product_names()
	assert products, 'Expected at least one inventory item'
	for product in products:
		assert product.strip(), 'Product name should not be empty'

	prices = inventory_page.page.locator('.inventory_item_price').all_text_contents()
	assert prices, 'Expected price labels for inventory items'
	for price in prices:
		assert price.strip().startswith('$'), f'Unexpected price label: {price}'


@then(parsers.parse('products should be sorted "{order}"'))
def verify_sorting(inventory_page, order):
	if 'alphabetically' in order:
		products = inventory_page.get_product_names()
		expected = sorted(products, reverse='descending' in order)
		assert products == expected
		return

	prices = [
		float(price.strip().replace('$', ''))
		for price in inventory_page.page.locator('.inventory_item_price').all_text_contents()
	]
	expected = sorted(prices, reverse='high to low' in order)
	assert prices == expected


@then('I should eventually see all products despite delays')
def verify_products_with_delay(inventory_page):
	time.sleep(2)
	assert inventory_page.get_product_count() == 6


@then('I should be on the product details page')
def verify_product_details_page(page):
	assert '/inventory-item.html' in page.url


@then(parsers.parse('the product details should show name "{product_name}"'))
def verify_product_details_name(page, product_name):
	assert page.locator('.inventory_details_name').text_content().strip() == product_name


@then('the product details should show a price')
def verify_product_details_price(page):
	price = page.locator('.inventory_details_price').text_content() or ''
	assert price.strip().startswith('$')


@then('the product details should show an add to cart button')
def verify_product_details_button(page):
	expect(page.locator("button[data-test*='add-to-cart']").first).to_be_visible()


@then('the cart badge should match the number of displayed products')
def verify_all_products_added(page, cart_widget):
	expected_count = getattr(page, '_displayed_product_count', 0)
	assert cart_widget.get_item_count() == expected_count
