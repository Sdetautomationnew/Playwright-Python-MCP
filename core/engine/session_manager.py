from playwright.sync_api import Browser, BrowserContext, Page


class SessionManager:
    def create_context(self, browser: Browser, record_video_dir: str = 'reports/videos') -> BrowserContext:
        return browser.new_context(record_video_dir=record_video_dir, ignore_https_errors=True)

    def create_page(self, context: BrowserContext, timeout_ms: int) -> Page:
        page = context.new_page()
        page.set_default_timeout(timeout_ms)
        return page
