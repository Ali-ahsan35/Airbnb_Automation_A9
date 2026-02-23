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

        # 1. Go to Airbnb
        self.page.goto("https://www.airbnb.com/")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)

        # 2. Clear cookies and storage
        self.page.context.clear_cookies()
        self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

        # 3. Reload after clearing
        self.page.reload()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)

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

        self.page.wait_for_timeout(1500)

        return f"Homepage loaded successfully. Country typed: {country}"

    def _close_popups(self):
        """Try to close any popups or modals"""
        try:
            close_btn = self.page.locator('[aria-label="Close"]')
            if close_btn.is_visible(timeout=3000):
                close_btn.click()
                self.page.wait_for_timeout(500)
        except:
            pass  # No popup found, continue