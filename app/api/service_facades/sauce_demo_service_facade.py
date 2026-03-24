from app.api.clients.sauce_demo_api_client import SauceDemoAPIClient

class SauceDemoServiceFacade:
    def __init__(self, client: SauceDemoAPIClient):
        self.client = client
