import pytest
from playwright.sync_api import Page
from core.config.runtime_config import EnvConfig
from app.ui.pages.login_page import LoginPage
from app.ui.pages.inventory_page import InventoryPage
from app.ui.pages.cart_page import CartPage
from app.ui.pages.checkout_page import CheckoutPage
from app.ui.components.cart_widget_component import CartWidgetComponent


def test_purchase_flow(page: Page, env_config: EnvConfig):
    """End-to-end test for complete purchase flow."""
    # Initialize page objects
    login_page = LoginPage(page, env_config)
    inventory_page = InventoryPage(page, env_config)
    cart_page = CartPage(page, env_config)
    checkout_page = CheckoutPage(page, env_config)
    cart_widget = CartWidgetComponent(page, env_config)

    # Login
    login_page.navigate_to(env_config.base_url)
    login_page.login("standard_user", "secret_sauce")

    # Add products to cart
    inventory_page.add_product_to_cart("Sauce Labs Backpack")
    inventory_page.add_product_to_cart("Sauce Labs Bike Light")

    # Go to cart
    cart_widget.go_to_cart()
    cart_page.proceed_to_checkout()

    # Fill checkout information
    checkout_page.fill_checkout_information("John", "Doe", "12345")
    checkout_page.continue_checkout()
    checkout_page.finish_checkout()

    # Verify success
    assert checkout_page.is_checkout_complete(), "Checkout should be complete"
    assert "Thank you for your order!" in checkout_page.get_completion_message()