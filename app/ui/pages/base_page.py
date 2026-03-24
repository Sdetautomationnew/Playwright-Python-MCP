import time
from typing import Optional, Any
from playwright.sync_api import Page, Locator, expect
from core.config.runtime_config import EnvConfig
from core.reporting.telemetry_client import get_logger


class BasePage:
    """
    Base page class implementing common page operations with robust wrappers.
    Enforces POM by providing abstracted interactions.
    Includes mobile-aware methods for touch emulation.
    """

    def __init__(self, page: Page, config: EnvConfig) -> None:
        """
        Initialize the base page.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        self.page = page
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    def wait_and_click(self, locator: Locator, timeout: Optional[int] = None) -> None:
        """
        Wait for locator to be visible and clickable, then click.

        Args:
            locator: Playwright Locator to click.
            timeout: Optional timeout in milliseconds. Falls back to config default if None.
        """
        effective_timeout = timeout or self.config.default_action_timeout_ms
        expect(locator).to_be_visible(timeout=effective_timeout)
        locator.click()

    def safe_fill(self, locator: Locator, value: str, timeout: Optional[int] = None) -> None:
        """
        Safely fill a text input after waiting for visibility.

        Args:
            locator: Playwright Locator to fill.
            value: Value to fill.
            timeout: Optional timeout in milliseconds.
        """
        effective_timeout = timeout or self.config.default_action_timeout_ms
        expect(locator).to_be_visible(timeout=effective_timeout)
        locator.fill(value)

    def get_text(self, locator: Locator, timeout: Optional[int] = None) -> str:
        """
        Get text content from a locator after waiting for visibility.

        Args:
            locator: Playwright Locator to get text from.
            timeout: Optional timeout in milliseconds.

        Returns:
            Text content of the locator.
        """
        effective_timeout = timeout or self.config.default_action_timeout_ms
        expect(locator).to_be_visible(timeout=effective_timeout)
        return locator.text_content() or ''

    def is_visible(self, locator: Locator, timeout: Optional[int] = None) -> bool:
        """
        Check if a locator is visible.

        Args:
            locator: Playwright Locator to check.
            timeout: Optional timeout in milliseconds.

        Returns:
            True if visible, False otherwise.
        """
        effective_timeout = timeout or self.config.default_action_timeout_ms
        try:
            expect(locator).to_be_visible(timeout=effective_timeout)
            return True
        except Exception:
            return False

    def tap_or_click(self, locator: Locator, timeout: Optional[int] = None) -> None:
        """
        Perform tap (if mobile/touch) or click based on device capabilities.
        Uses page.tap() for touch devices, falls back to click for desktop.

        Args:
            locator: Playwright Locator to interact with.
            timeout: Optional timeout in milliseconds.
        """
        effective_timeout = timeout or self.config.default_action_timeout_ms
        expect(locator).to_be_visible(timeout=effective_timeout)
        # Check if the page context has touch capabilities (from device preset)
        if hasattr(self.page.context, '_options') and self.page.context._options.get('hasTouch', False):
            locator.tap()
        else:
            locator.click()

    def wait_for_load_state(self, state: str = 'networkidle', timeout: Optional[int] = None) -> None:
        """
        Wait for the page to reach a specific load state.

        Args:
            state: Load state to wait for ('load', 'domcontentloaded', 'networkidle').
            timeout: Optional timeout in milliseconds.
        """
        effective_timeout = timeout or self.config.default_navigation_timeout_ms
        self.page.wait_for_load_state(state, timeout=effective_timeout)

    def navigate_to(self, url: str, timeout: Optional[int] = None) -> None:
        """
        Navigate to a URL with timeout.

        Args:
            url: URL to navigate to.
            timeout: Optional timeout in milliseconds.
        """
        effective_timeout = timeout or self.config.default_navigation_timeout_ms
        self.page.goto(url, timeout=effective_timeout)
        self.wait_for_load_state(timeout=effective_timeout)

    def retry_action(self, action: callable, max_retries: int = 3, delay: float = 1.0) -> Any:
        """
        Retry a flaky action with exponential backoff.

        Args:
            action: Callable to retry.
            max_retries: Maximum number of retries.
            delay: Initial delay between retries.

        Returns:
            Result of the action if successful.

        Raises:
            Exception: If all retries fail.
        """
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                return action()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    self.logger.warning(f"Action failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
        raise last_exception