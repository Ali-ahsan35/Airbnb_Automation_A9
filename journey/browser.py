import os
from django.conf import settings
from playwright.sync_api import sync_playwright


class BrowserManager:

    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.console_logs = []
        self.network_logs = []

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )

        # Clear cookies and cache on start
        self.context.clear_cookies()

        self.page = self.context.new_page()

        # Attach console log listener
        self.page.on("console", self._capture_console)

        # Attach network log listener
        self.page.on("response", self._capture_network)

        return self.page

    def _capture_console(self, msg):
        self.console_logs.append({
            "type": msg.type,
            "text": msg.text
        })

    def _capture_network(self, response):
        self.network_logs.append({
            "url": response.url,
            "status": response.status
        })

    def take_screenshot(self, step_name):
        """Takes screenshot and returns the saved file path"""
        screenshots_dir = settings.SCREENSHOTS_DIR
        os.makedirs(screenshots_dir, exist_ok=True)

        filename = f"{step_name}.png"
        filepath = os.path.join(screenshots_dir, filename)

        self.page.screenshot(path=filepath, full_page=True)
        return filepath

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()