from pytest_bdd import parsers, then, when
from playwright.sync_api import expect


def _remember_product(page, product_name):
	setattr(page, '_last_product_name', product_name)


def _product_locator(page, product_name):
	return page.locator('.inventory_item').filter(has_text=product_name)


@when(parsers.parse('I add "{product_name}" to the cart'))
@when(parsers.parse('I add "{product_name}" to cart'))
def add_product_to_cart(inventory_page, cart_widget, product_name):
	inventory_page.add_product_to_cart(product_name)
	_remember_product(inventory_page.page, product_name)
	assert cart_widget.get_item_count() != 0


@when(parsers.parse('I remove "{product_name}" from the cart'))
def remove_product_from_cart(inventory_page, product_name):
	inventory_page.remove_product_from_cart(product_name)
	_remember_product(inventory_page.page, product_name)


@when(parsers.parse('I remove "{product_name}" from the cart page'))
def remove_product_from_cart_page(cart_page, product_name):
	cart_page.remove_item_from_cart(product_name)
	_remember_product(cart_page.page, product_name)


@when('I navigate to cart page')
def navigate_to_cart(cart_widget):
	cart_widget.go_to_cart()


@when('I continue shopping')
def continue_shopping(page):
	page.locator('#continue-shopping').click()


@then(parsers.parse('the cart badge should show "{count}"'))
def verify_cart_badge(cart_widget, count):
	assert str(cart_widget.get_item_count()) == count


@then('the product should be marked as added')
def verify_product_added(page):
	product_name = getattr(page, '_last_product_name', '')
	product_locator = _product_locator(page, product_name)
	expect(product_locator.locator("button:has-text('Remove')")).to_be_visible()


@then('the product should be available for adding again')
def verify_product_available(page):
	product_name = getattr(page, '_last_product_name', '')
	product_locator = _product_locator(page, product_name)
	expect(product_locator.locator("button:has-text('Add to cart')")).to_be_visible()


@then(parsers.parse('I should see "{product_name}" in the cart'))
def verify_product_in_cart(page, cart_widget, product_name):
	if 'cart' not in page.url:
		cart_widget.go_to_cart()
		page.wait_for_url(lambda url: 'cart' in url, timeout=5000)

	cart_items = page.locator('.cart_item .inventory_item_name').all_text_contents()
	assert product_name in cart_items


@then('the cart should contain 1 item')
def verify_single_cart_item(cart_page):
	assert cart_page.get_cart_item_count() == 1


@then(parsers.parse('the cart should contain {count:d} items'))
def verify_cart_item_count(cart_page, count):
	assert cart_page.get_cart_item_count() == count
