from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig
from app.ui.components.checkout_form_component import CheckoutFormComponent


class CheckoutPage(BasePage):
    """
    Page Object Model for the Sauce Demo checkout pages.
    Composes checkout form component.
    """

    # Locators
    CHECKOUT_SUMMARY = ".checkout_summary_container"
    FINISH_BUTTON = "#finish"
    COMPLETE_MESSAGE = ".complete-header"

    def __init__(self, page: Locator, config: EnvConfig) -> None:
        """
        Initialize the checkout page.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)
        self.checkout_form = CheckoutFormComponent(page, config)

    def fill_checkout_information(self, first_name: str, last_name: str, zip_code: str) -> None:
        """
        Fill checkout information using the form component.

        Args:
            first_name: First name.
            last_name: Last name.
            zip_code: Zip code.
        """
        self.checkout_form.fill_information(first_name, last_name, zip_code)

    def continue_checkout(self) -> None:
        """
        Continue to checkout summary.
        """
        self.checkout_form.continue_checkout()

    def finish_checkout(self) -> None:
        """
        Finish the checkout process.
        """
        self.tap_or_click(self.page.locator(self.FINISH_BUTTON))

    def get_completion_message(self) -> str:
        """
        Get the order completion message.

        Returns:
            Completion message text.
        """
        return self.get_text(self.page.locator(self.COMPLETE_MESSAGE))

    def is_checkout_complete(self) -> bool:
        """
        Check if checkout is complete.

        Returns:
            True if complete, False otherwise.
        """
        return self.is_visible(self.page.locator(self.COMPLETE_MESSAGE))