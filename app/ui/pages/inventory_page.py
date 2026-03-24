from typing import List
from playwright.sync_api import Locator
from app.ui.pages.base_page import BasePage
from core.config.runtime_config import EnvConfig
from app.ui.components.filter_sort_component import FilterSortComponent
from app.ui.components.product_card_component import ProductCardComponent


class InventoryPage(BasePage):
    """
    Page Object Model for the Sauce Demo inventory page.
    Composes components for filter/sort and product cards.
    """

    # Locators
    INVENTORY_CONTAINER = ".inventory_list"
    INVENTORY_ITEMS = ".inventory_item"

    def __init__(self, page: Locator, config: EnvConfig) -> None:
        """
        Initialize the inventory page.

        Args:
            page: Playwright Page instance.
            config: Environment configuration.
        """
        super().__init__(page, config)
        self.filter_sort = FilterSortComponent(page, config)
        self.product_cards = []  # Will be populated dynamically

    def get_product_count(self) -> int:
        """
        Get the number of products displayed.

        Returns:
            Number of products.
        """
        return len(self.page.locator(self.INVENTORY_ITEMS).all())

    def get_product_names(self) -> List[str]:
        """
        Get list of all product names.

        Returns:
            List of product names.
        """
        locators = self.page.locator(self.INVENTORY_ITEMS).all()
        return [self.get_text(locator.locator(".inventory_item_name")) for locator in locators]

    def add_product_to_cart(self, product_name: str) -> None:
        """
        Add a specific product to cart by name.

        Args:
            product_name: Name of the product to add.
        """
        product_locator = self.page.locator(self.INVENTORY_ITEMS).filter(has_text=product_name)
        add_button = product_locator.locator("button:has-text('Add to cart')")
        self.tap_or_click(add_button)

    def remove_product_from_cart(self, product_name: str) -> None:
        """
        Remove a specific product from cart by name.

        Args:
            product_name: Name of the product to remove.
        """
        product_locator = self.page.locator(self.INVENTORY_ITEMS).filter(has_text=product_name)
        remove_button = product_locator.locator("button:has-text('Remove')")
        self.tap_or_click(remove_button)

    def sort_products(self, sort_option: str) -> None:
        """
        Sort products using the filter/sort component.

        Args:
            sort_option: Sort option (e.g., 'az', 'za', 'lohi', 'hilo').
        """
        self.filter_sort.select_sort_option(sort_option)