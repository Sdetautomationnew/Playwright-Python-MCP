from .product import Product


class ProductValidator:
    """Validator for Product model."""

    @staticmethod
    def validate(product: Product) -> bool:
        if not product.name or product.price < 0:
            return False
        return True

    @staticmethod
    def validate_price(price: float) -> bool:
        return price >= 0