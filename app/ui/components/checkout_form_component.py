from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig


class CheckoutFormComponent(BasePage):
    """
    Component for checkout information form.
    """

    # Locators
    FIRST_NAME_INPUT = "#first-name"
    LAST_NAME_INPUT = "#last-name"
    ZIP_CODE_INPUT = "#postal-code"
    CONTINUE_BUTTON = "#continue"
    ERROR_MESSAGE = ".error-message-container"

    def __init__(self, page: Locator, config: EnvConfig) -> None:
        """
        Initialize the checkout form component.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)

    def fill_information(self, first_name: str, last_name: str, zip_code: str) -> None:
        """
        Fill checkout information fields.

        Args:
            first_name: First name.
            last_name: Last name.
            zip_code: Zip code.
        """
        self.safe_fill(self.page.locator(self.FIRST_NAME_INPUT), first_name)
        self.safe_fill(self.page.locator(self.LAST_NAME_INPUT), last_name)
        self.safe_fill(self.page.locator(self.ZIP_CODE_INPUT), zip_code)

    def continue_checkout(self) -> None:
        """
        Click continue button.
        """
        self.tap_or_click(self.page.locator(self.CONTINUE_BUTTON))

    def get_error_message(self) -> str:
        """
        Get error message if present.

        Returns:
            Error message or empty string.
        """
        if self.is_visible(self.page.locator(self.ERROR_MESSAGE)):
            return self.get_text(self.page.locator(self.ERROR_MESSAGE))
        return ""