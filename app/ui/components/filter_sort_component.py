from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig


class FilterSortComponent(BasePage):
    """
    Component for product filtering and sorting.
    """

    # Locators
    SORT_DROPDOWN = ".product_sort_container"

    def __init__(self, page: Locator, config: EnvConfig) -> None:
        """
        Initialize the filter/sort component.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)

    def select_sort_option(self, option_value: str) -> None:
        """
        Select a sort option from the dropdown.

        Args:
            option_value: Value of the sort option (e.g., 'az', 'za', 'lohi', 'hilo').
        """
        self.page.locator(self.SORT_DROPDOWN).select_option(option_value)