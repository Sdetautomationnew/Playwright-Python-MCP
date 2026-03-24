from typing import Dict, Any, Optional
from app.api.clients.base_api_client import BaseAPIClient
from core.config.runtime_config import EnvConfig
from core.reporting.telemetry_client import get_logger


class SauceDemoAPIClient(BaseAPIClient):
    """
    Specialized API client for Sauce Demo application.
    Provides methods for testing product, cart, checkout, and authentication endpoints.
    """

    def __init__(self, config: EnvConfig, base_url: Optional[str] = None) -> None:
        """
        Initialize Sauce Demo API client.

        Args:
            config: Environment configuration.
            base_url: Base URL for API. Defaults to config.api_url.
        """
        super().__init__(config, base_url)
        self.auth_token: Optional[str] = None
        self.logger = get_logger(self.__class__.__name__)

    def set_auth_token(self, token: str) -> None:
        """
        Set authentication token for subsequent requests.

        Args:
            token: Authorization token.
        """
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_auth_token(self) -> None:
        """Clear authentication token."""
        self.auth_token = None
        self.session.headers.pop("Authorization", None)

    # ==================== AUTHENTICATION ENDPOINTS ====================

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and get session token.

        Args:
            username: User username.
            password: User password.

        Returns:
            Response containing token and user info.
        """
        response = self.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.set_auth_token(data.get("token"))
        return response

    def logout(self) -> Dict[str, Any]:
        """
        Logout current user.

        Returns:
            Response confirming logout.
        """
        response = self.post("/api/v1/auth/logout")
        self.clear_auth_token()
        return response

    # ==================== PRODUCT ENDPOINTS ====================

    def get_products(self, sort: Optional[str] = None, order: Optional[str] = None,
                    category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of products with optional filtering and sorting.

        Args:
            sort: Sort field (price, name, etc.)
            order: Sort order (asc, desc)
            category: Product category filter

        Returns:
            Response containing products list.
        """
        params = {}
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
        if category:
            params["category"] = category

        endpoint = "/api/v1/products"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{endpoint}?{param_str}"

        response = self.get(endpoint)
        return response

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """
        Get specific product details.

        Args:
            product_id: Product ID.

        Returns:
            Response containing product details.
        """
        response = self.get(f"/api/v1/products/{product_id}")
        return response

    def get_product_filters(self) -> Dict[str, Any]:
        """
        Get available product filters and sorting options.

        Returns:
            Response containing filters and sorting options.
        """
        response = self.get("/api/v1/products/filters")
        return response

    # ==================== CART ENDPOINTS ====================

    def add_to_cart(self, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """
        Add product to shopping cart.

        Args:
            product_id: Product ID to add.
            quantity: Quantity to add (default: 1).

        Returns:
            Response confirming addition to cart.
        """
        response = self.post(
            "/api/v1/cart/add",
            json={"product_id": product_id, "quantity": quantity}
        )
        return response

    def remove_from_cart(self, product_id: int) -> Dict[str, Any]:
        """
        Remove product from shopping cart.

        Args:
            product_id: Product ID to remove.

        Returns:
            Response confirming removal from cart.
        """
        response = self.delete(f"/api/v1/cart/items/{product_id}")
        return response

    def get_cart(self) -> Dict[str, Any]:
        """
        Get current cart contents.

        Returns:
            Response containing cart items and totals.
        """
        response = self.get("/api/v1/cart")
        return response

    def update_cart_item(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """
        Update product quantity in cart.

        Args:
            product_id: Product ID to update.
            quantity: New quantity.

        Returns:
            Response confirming quantity update.
        """
        response = self.put(
            f"/api/v1/cart/items/{product_id}",
            json={"quantity": quantity}
        )
        return response

    def clear_cart(self) -> Dict[str, Any]:
        """
        Clear all items from cart.

        Returns:
            Response confirming cart cleared.
        """
        response = self.delete("/api/v1/cart")
        return response

    # ==================== CHECKOUT ENDPOINTS ====================

    def get_checkout_summary(self) -> Dict[str, Any]:
        """
        Get checkout summary before payment.

        Returns:
            Response containing checkout summary with items and totals.
        """
        response = self.get("/api/v1/checkout/summary")
        return response

    def process_checkout(self, first_name: str, last_name: str, zip_code: str) -> Dict[str, Any]:
        """
        Process checkout and create order.

        Args:
            first_name: Customer first name.
            last_name: Customer last name.
            zip_code: Customer zip code.

        Returns:
            Response with order confirmation.
        """
        response = self.post(
            "/api/v1/checkout",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "zip_code": zip_code
            }
        )
        return response

    def confirm_order(self, order_id: str) -> Dict[str, Any]:
        """
        Confirm order completion.

        Args:
            order_id: Order ID to confirm.

        Returns:
            Response with order confirmation.
        """
        response = self.post(f"/api/v1/checkout/confirm/{order_id}")
        return response

    # ==================== INVENTORY ENDPOINTS ====================

    def get_inventory_status(self, product_id: int) -> Dict[str, Any]:
        """
        Get inventory status for a product.

        Args:
            product_id: Product ID.

        Returns:
            Response containing inventory information.
        """
        response = self.get(f"/api/v1/inventory/{product_id}")
        return response

    def get_all_inventory(self) -> Dict[str, Any]:
        """
        Get inventory status for all products.

        Returns:
            Response containing all inventory information.
        """
        response = self.get("/api/v1/inventory")
        return response
