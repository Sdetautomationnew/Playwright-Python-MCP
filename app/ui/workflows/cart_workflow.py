from app.ui.components.cart_widget_component import CartWidgetComponent
from app.ui.pages.inventory_page import InventoryPage

class CartWorkflow:
    def __init__(self, inventory_page: InventoryPage, cart_widget: CartWidgetComponent):
        self.inventory_page = inventory_page
        self.cart_widget = cart_widget

    def add_product(self, product_name):
        self.inventory_page.add_product_to_cart(product_name)
        return self.cart_widget.get_item_count()

    def open_cart(self):
        self.cart_widget.go_to_cart()
