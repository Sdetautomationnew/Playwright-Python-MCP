from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig


class ProductCardComponent(BasePage):
    """
    Component for individual product cards.
    """

    def __init__(self, page: Locator, config: EnvConfig, product_locator: Locator) -> None:
        """
        Initialize the product card component.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
            product_locator: Locator for the specific product card.
        """
        super().__init__(page, config)
        self.product_locator = product_locator

    def get_product_name(self) -> str:
        """
        Get the product name.

        Returns:
            Product name.
        """
        return self.get_text(self.product_locator.locator(".inventory_item_name"))

    def get_product_price(self) -> str:
        """
        Get the product price.

        Returns:
            Product price.
        """
        return self.get_text(self.product_locator.locator(".inventory_item_price"))

    def add_to_cart(self) -> None:
        """
        Add product to cart.
        """
        add_button = self.product_locator.locator("button:has-text('Add to cart')")
        self.tap_or_click(add_button)

    def remove_from_cart(self) -> None:
        """
        Remove product from cart.
        """
        remove_button = self.product_locator.locator("button:has-text('Remove')")
        self.tap_or_click(remove_button)