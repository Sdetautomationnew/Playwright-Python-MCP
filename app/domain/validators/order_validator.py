from .order import Order


class OrderValidator:
    """Validator for Order model."""

    @staticmethod
    def validate(order: Order) -> bool:
        if not order.user_id or not order.products:
            return False
        if order.total_price < 0:
            return False
        return True