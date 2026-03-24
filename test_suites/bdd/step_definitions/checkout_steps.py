from pytest_bdd import given, parsers, then, when


def _navigate_to_checkout_step_one(page):
	if 'checkout-step-one' in page.url:
		return

	if 'cart' not in page.url:
		page.locator('.shopping_cart_link').click()
		page.wait_for_url(lambda url: 'cart' in url, timeout=5000)

	page.locator("[data-test='checkout']").click()
	page.wait_for_url(lambda url: 'checkout-step-one' in url, timeout=5000)


def _valid_checkout_info(checkout_provider):
	info = next((item for item in checkout_provider.load_checkout_info() if item['expected_success']), None)
	assert info, 'No valid checkout info found'
	return info


@given(parsers.parse('I have added "{product_name}" to the cart'))
def add_product_to_cart_setup(inventory_page, product_name):
	inventory_page.add_product_to_cart(product_name)


@when('I proceed to checkout')
def proceed_to_checkout(cart_page):
	_navigate_to_checkout_step_one(cart_page.page)


@when('I enter valid checkout information')
def enter_valid_checkout_info(checkout_page, checkout_provider):
	_navigate_to_checkout_step_one(checkout_page.page)
	valid_info = _valid_checkout_info(checkout_provider)
	checkout_page.fill_checkout_information(
		valid_info['first_name'],
		valid_info['last_name'],
		valid_info['zip_code'],
	)


@when('I leave the first name blank')
def leave_first_name_blank(checkout_page, checkout_provider):
	_navigate_to_checkout_step_one(checkout_page.page)
	valid_info = _valid_checkout_info(checkout_provider)
	checkout_page.fill_checkout_information('', valid_info['last_name'], valid_info['zip_code'])


@when('I leave the last name blank')
def leave_last_name_blank(checkout_page, checkout_provider):
	_navigate_to_checkout_step_one(checkout_page.page)
	valid_info = _valid_checkout_info(checkout_provider)
	checkout_page.fill_checkout_information(valid_info['first_name'], '', valid_info['zip_code'])


@when('I leave the zip code blank')
def leave_zip_code_blank(checkout_page, checkout_provider):
	_navigate_to_checkout_step_one(checkout_page.page)
	valid_info = _valid_checkout_info(checkout_provider)
	checkout_page.fill_checkout_information(valid_info['first_name'], valid_info['last_name'], '')


@when(parsers.parse('I enter "{first_name}" as first name and "{last_name}" as last name'))
def enter_first_and_last_name(checkout_page, first_name, last_name):
	_navigate_to_checkout_step_one(checkout_page.page)
	checkout_page.page.locator('#first-name').fill(first_name)
	checkout_page.page.locator('#last-name').fill(last_name)


@when(parsers.parse('I enter "{zip_code}" as zip code'))
def enter_zip_code(checkout_page, zip_code):
	_navigate_to_checkout_step_one(checkout_page.page)
	checkout_page.page.locator('#postal-code').fill(zip_code)


@when('I try to continue')
def try_continue_checkout(checkout_page):
	checkout_page.continue_checkout()


@when('I complete the purchase')
def complete_purchase(checkout_page):
	if 'checkout-step-one' in checkout_page.page.url:
		checkout_page.continue_checkout()
		checkout_page.page.locator('#finish').wait_for(state='visible', timeout=15000)
	checkout_page.finish_checkout()


@then('I should be on the checkout information page')
def verify_checkout_information_page(checkout_page):
	assert 'checkout-step-one' in checkout_page.page.url


@then('I should see the checkout information form')
def verify_checkout_information_form(checkout_page):
	assert checkout_page.page.locator('#first-name').is_visible()
	assert checkout_page.page.locator('#last-name').is_visible()
	assert checkout_page.page.locator('#postal-code').is_visible()


@then('I should be on the checkout overview page')
def verify_checkout_overview_page(checkout_page):
	assert 'checkout-step-two' in checkout_page.page.url


@then('I should see the order confirmation message')
def verify_order_confirmation(checkout_page):
	assert checkout_page.is_checkout_complete()


@then('the cart should be empty')
def verify_cart_empty(cart_widget):
	assert cart_widget.get_item_count() == 0
