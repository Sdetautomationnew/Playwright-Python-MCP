from playwright.sync_api import Page
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig


class LoginPage(BasePage):
    """
    Page Object Model for the Sauce Demo login page.
    """

    # Locators
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = ".error-message-container"

    def __init__(self, page: Page, config: EnvConfig) -> None:
        """
        Initialize the login page.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)

    def login(self, username: str, password: str) -> None:
        """
        Perform login with given credentials.

        Args:
            username: Username to enter.
            password: Password to enter.
        """
        self.safe_fill(self.page.locator(self.USERNAME_INPUT), username)
        self.safe_fill(self.page.locator(self.PASSWORD_INPUT), password)
        self.wait_and_click(self.page.locator(self.LOGIN_BUTTON))

    def get_error_message(self) -> str:
        """
        Get the error message if present.

        Returns:
            Error message text or empty string.
        """
        try:
            # Try the main error message container first
            error_locator = self.page.locator(self.ERROR_MESSAGE)
            if error_locator.count() > 0:
                text = error_locator.text_content()
                return text.strip() if text else ''
        except:
            pass
        
        # Try h3 element (standard sauce demo error location)
        try:
            h3_locator = self.page.locator("h3")
            if h3_locator.count() > 0:
                text = h3_locator.text_content()
                if text and "Epic sadface" in text:
                    return text.strip()
        except:
            pass
        
        # Try common error message classes
        try:
            error_locator = self.page.locator(".error-message")
            if error_locator.count() > 0:
                text = error_locator.text_content()
                return text.strip() if text else ''
        except:
            pass
        
        return ''

    def is_login_successful(self) -> bool:
        """
        Check if login was successful by checking for inventory page elements.

        Returns:
            True if login successful, False otherwise.
        """
        # Assuming inventory page has a specific element, e.g., inventory container
        return self.is_visible(self.page.locator(".inventory_list"))