from playwright.sync_api import sync_playwright

class BrowserEngine:
    def __init__(self, config):
        self.config = config

    def launch(self, headed=False):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=not headed)
        return playwright, browser
