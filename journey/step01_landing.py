# journey/step01_landing.py
import random
import time
from journey.base_step import BaseStep


class Step01Landing(BaseStep):

    # Top 20 countries list
    COUNTRIES = [
        "United States", "China", "India", "Brazil", "Russia",
        "Germany", "United Kingdom", "France", "Japan", "Canada",
        "Italy", "South Korea", "Australia", "Spain", "Mexico",
        "Indonesia", "Netherlands", "Saudi Arabia", "Turkey", "Switzerland"
    ]

    @property
    def step_number(self):
        return 1

    @property
    def test_case(self):
        return "Website Landing and Initial Search Setup"

    def execute(self):

         # 1. Clear cookies BEFORE loading (context level, no page needed)
        self.page.context.clear_cookies()
        # # 1. Go to Airbnb
        # self.page.goto("https://www.airbnb.com/")
        # self.page.wait_for_load_state("domcontentloaded")
        # self.page.wait_for_timeout(3000)

        # 2. Go to Airbnb (only once)
        self.page.goto("https://www.airbnb.com/")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)

        # 2. Clear cookies and storage
        # self.page.context.clear_cookies()
        # self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

        # 3. Clear local storage AFTER first load (needs page to exist)
        self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

        # 3. Reload after clearing
        # self.page.reload()
        # self.page.wait_for_load_state("domcontentloaded")
        # self.page.wait_for_timeout(3000)

        # 4. Close any popups
        self._close_popups()

        # 5. Confirm homepage loaded
        assert "airbnb" in self.page.url.lower(), "Homepage did not load correctly"

        # 6. Select a random country
        country = random.choice(self.COUNTRIES)
        self.context['country'] = country
        print(f"Selected country: {country}")

        # 7. Click the search field
        search_field = self.page.locator('#bigsearch-query-location-input')
        search_field.wait_for(state="visible", timeout=10000)
        search_field.click()
        self.page.wait_for_timeout(1000)

        # 8. Type like a real user character by character
        for char in country:
            search_field.type(char, delay=100)

        self.page.wait_for_timeout(5000)

        return f"Homepage loaded successfully. Country typed: {country}"

    def _close_popups(self):
        """Try to close any popups or modals"""
        
        # List of possible close/dismiss buttons
        popup_selectors = [
            '[aria-label="Close"]',
            'button[data-testid="close-button"]',
            '//button[text()="Got it"]',
            '//button[text()="OK"]',
            '//button[text()="Accept"]',
            '//button[contains(text(), "Got it")]',
            '//button[contains(text(), "Close")]',
        ]

        for selector in popup_selectors:
            try:
                # Handle both CSS and XPath selectors
                if selector.startswith('//'):
                    btn = self.page.locator(f'xpath={selector}')
                else:
                    btn = self.page.locator(selector)

                if btn.is_visible(timeout=2000):
                    btn.click()
                    print(f"Closed popup with: {selector}")
                    self.page.wait_for_timeout(1000)
            except:
                continue