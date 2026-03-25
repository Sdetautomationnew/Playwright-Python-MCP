from playwright.sync_api import sync_playwright

class BrowserEngine:
    def __init__(self, config):
        self.config = config

    def launch(self, headed=False):
        playwright = sync_playwright().start()
        browser_name = "chromium"
        if self.config and hasattr(self.config, "get_env_var"):
            browser_name = (self.config.get_env_var("BROWSER", "chromium") or "chromium").lower().strip()
        if browser_name == "chrome":
            browser_name = "chromium"

        launcher = {
            "chromium": playwright.chromium,
            "firefox": playwright.firefox,
            "webkit": playwright.webkit,
        }.get(browser_name)

        if launcher is None:
            raise ValueError(
                f'Unsupported BROWSER="{browser_name}". Expected one of: chromium, firefox, webkit.'
            )

        browser = launcher.launch(headless=not headed)
        return playwright, browser
