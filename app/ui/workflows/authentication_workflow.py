from app.ui.pages.login_page import LoginPage

class AuthenticationWorkflow:
    def __init__(self, login_page: LoginPage):
        self.login_page = login_page

    def login_as(self, username, password):
        self.login_page.navigate_to(self.login_page.config.base_url)
        self.login_page.login(username, password)
