from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig


class HeaderComponent(BasePage):
    """
    Component for the header section including menu, cart icon, logout.
    """

    # Locators
    MENU_BUTTON = "#react-burger-menu-btn"
    LOGOUT_LINK = "#logout_sidebar_link"
    CART_ICON = ".shopping_cart_link"
    CART_BADGE = ".shopping_cart_badge"

    def __init__(self, page: Locator, config: EnvConfig) -> None:
        """
        Initialize the header component.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)

    def open_menu(self) -> None:
        """
        Open the hamburger menu.
        """
        self.tap_or_click(self.page.locator(self.MENU_BUTTON))

    def logout(self) -> None:
        """
        Perform logout.
        """
        self.open_menu()
        self.tap_or_click(self.page.locator(self.LOGOUT_LINK))

    def go_to_cart(self) -> None:
        """
        Navigate to cart page.
        """
        self.tap_or_click(self.page.locator(self.CART_ICON))

    def get_cart_badge_count(self) -> str:
        """
        Get the cart badge count.

        Returns:
            Badge count as string, or empty if no badge.
        """
        if self.is_visible(self.page.locator(self.CART_BADGE)):
            return self.get_text(self.page.locator(self.CART_BADGE))
        return "0"