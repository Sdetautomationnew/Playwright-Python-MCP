from app.ui.pages.checkout_page import CheckoutPage
from app.ui.workflows.cart_workflow import CartWorkflow

class PurchaseWorkflow:
    def __init__(self, cart_workflow: CartWorkflow, checkout_page: CheckoutPage):
        self.cart_workflow = cart_workflow
        self.checkout_page = checkout_page

    def purchase(self, product_name, first_name, last_name, zip_code):
        self.cart_workflow.add_product(product_name)
        self.cart_workflow.open_cart()
        self.checkout_page.proceed_to_checkout()
        self.checkout_page.fill_checkout_information(first_name, last_name, zip_code)
        self.checkout_page.continue_checkout()
        self.checkout_page.finish_checkout()
