from pytest_bdd import given, parsers, then, when
from playwright.sync_api import expect


@given('I am on the login page')
def navigate_to_login(login_page):
 login_page.navigate_to(login_page.config.base_url)


@given(parsers.parse('I am logged in as "{username}"'))
def login_as_user(login_page, user_provider, username):
 login_page.navigate_to(login_page.config.base_url)
 user = next((candidate for candidate in user_provider.load_users() if candidate['username'] == username), None)
 assert user, f'User {username} not found in data'
 login_page.login(user['username'], user['password'])
 expect(login_page.page.locator('.inventory_list')).to_be_visible()


@when(parsers.parse('I enter username "{username}" and password "{password}"'))
def enter_credentials(login_page, username, password):
 login_page.safe_fill(login_page.page.locator('#user-name'), username)
 login_page.safe_fill(login_page.page.locator('#password'), password)


@when(parsers.parse('I enter password "{password}" with an empty username'))
def enter_password_with_empty_username(login_page, password):
 login_page.safe_fill(login_page.page.locator('#user-name'), '')
 login_page.safe_fill(login_page.page.locator('#password'), password)


@when('I click the login button')
def click_login_button(login_page):
 login_page.wait_and_click(login_page.page.locator('#login-button'))


@then('I should be redirected to the inventory page')
def verify_inventory_page(login_page):
 expect(login_page.page.locator('.inventory_list')).to_be_visible()


@then('I should see products displayed')
def verify_products_displayed(inventory_page):
 assert inventory_page.get_product_count() != 0


@then('I should remain on the login page')
def verify_remain_on_login_page(login_page):
 expect(login_page.page.locator('#login-button')).to_be_visible()
