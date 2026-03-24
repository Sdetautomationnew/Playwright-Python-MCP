class CheckoutValidator:
    def is_valid(self, details):
        return all([details.first_name, details.last_name, details.zip_code])
