from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig


class CartWidgetComponent(BasePage):
    """
    Component for the cart widget/badge in header.
    """

    # Locators
    CART_LINK = ".shopping_cart_link"
    CART_BADGE = ".shopping_cart_badge"

    def __init__(self, page: Locator, config: EnvConfig) -> None:
        """
        Initialize the cart widget component.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)

    def get_item_count(self) -> int:
        """
        Get the number of items in cart from badge.

        Returns:
            Item count, 0 if no badge.
        """
        if self.is_visible(self.page.locator(self.CART_BADGE)):
            return int(self.get_text(self.page.locator(self.CART_BADGE)))
        return 0

    def go_to_cart(self) -> None:
        """
        Click cart link to go to cart page.
        """
        self.tap_or_click(self.page.locator(self.CART_LINK))