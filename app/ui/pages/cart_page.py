from typing import List
from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig
from app.ui.components.product_card_component import ProductCardComponent


class CartPage(BasePage):
    """
    Page Object Model for the Sauce Demo cart page.
    """

    # Locators
    CART_ITEMS = ".cart_item"
    CART_ITEM_NAME = ".inventory_item_name"
    CART_ITEM_PRICE = ".inventory_item_price"
    REMOVE_BUTTON = "button:has-text('Remove')"
    CHECKOUT_BUTTON = "#checkout"

    def __init__(self, page: Locator, config: EnvConfig) -> None:
        """
        Initialize the cart page.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)

    def get_cart_item_count(self) -> int:
        """
        Get the number of items in the cart.

        Returns:
            Number of cart items.
        """
        return len(self.page.locator(self.CART_ITEMS).all())

    def get_cart_item_names(self) -> List[str]:
        """
        Get list of cart item names.

        Returns:
            List of item names in cart.
        """
        return [self.get_text(item.locator(self.CART_ITEM_NAME)) for item in self.page.locator(self.CART_ITEMS).all()]

    def remove_item_from_cart(self, item_name: str) -> None:
        """
        Remove a specific item from cart by name.

        Args:
            item_name: Name of the item to remove.
        """
        item_locator = self.page.locator(self.CART_ITEMS).filter(has_text=item_name)
        remove_button = item_locator.locator(self.REMOVE_BUTTON)
        self.tap_or_click(remove_button)

    def proceed_to_checkout(self) -> None:
        """
        Click the checkout button to proceed.
        """
        self.tap_or_click(self.page.locator(self.CHECKOUT_BUTTON))