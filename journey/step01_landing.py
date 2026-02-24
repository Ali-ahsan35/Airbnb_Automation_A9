import random
import threading
from journey.base_step import BaseStep
from automation.models import AutoSuggestion


class Step01Landing(BaseStep):

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

        # 1. Clear cookies BEFORE loading
        self.page.context.clear_cookies()

        # 2. Go to Airbnb once
        self.page.goto("https://www.airbnb.com/")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)

        # 3. Clear local storage
        self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

        # 4. Close any popups BEFORE clicking search
        self._close_popups()

        # 5. Confirm homepage loaded
        assert "airbnb" in self.page.url.lower(), "Homepage did not load correctly"
        print(f"Page URL: {self.page.url}")
        print(f"Page title: {self.page.title()}")

        # 6. Select a random country
        country = random.choice(self.COUNTRIES)
        self.context['country'] = country
        print(f"Selected country: {country}")

        # 7. Click the search field
        search_field = self.page.locator('#bigsearch-query-location-input')
        search_field.wait_for(state="visible", timeout=10000)
        search_field.click()
        self.page.wait_for_timeout(1000)

        # 8. Type like a real user
        for char in country:
            search_field.type(char, delay=100)
        self.page.wait_for_timeout(2000)

        # 9. Close Got it popup if appears AFTER typing
        try:
            got_it = self.page.locator('//button[contains(text(), "Got it")]')
            if got_it.is_visible(timeout=3000):
                got_it.click()
                print("Closed Got it popup")
                self.page.wait_for_timeout(500)
                search_field.fill('')
                self.page.wait_for_timeout(300)
                for char in country:
                    search_field.type(char, delay=100)
                self.page.wait_for_timeout(2000)
        except:
            pass

        # 10. Wait for suggestions
        suggestion_list = self.page.locator('#bigsearch-query-location-listbox')
        suggestion_list.wait_for(state="visible", timeout=10000)

        # 11. Wait extra time for ALL suggestions to fully render
        self.page.wait_for_timeout(2000)
        print("Suggestions visible")

        # 12. Capture suggestions using inner_text on whole option
        # Use the full option text instead of a child class (more reliable)
        suggestions = self.page.locator(
            '#bigsearch-query-location-listbox [role="option"]'
        ).all()
        assert len(suggestions) > 0, "No suggestions found"
        print(f"Found {len(suggestions)} suggestions")

        suggestion_data = []
        for i, suggestion in enumerate(suggestions):
            try:
                # Wait for each suggestion to be visible first
                suggestion.wait_for(state="visible", timeout=5000)

                # Use inner_text on the whole option — more reliable than child class
                # full_text = suggestion.inner_text().strip()
                # Clean up text (remove newlines)
                # text = ' '.join(full_text.split())

                try:
                    # Try getting just the first text div
                    text_div = suggestion.locator('div[class*="t5i37sl"]')
                    if text_div.count() > 0:
                        text = text_div.first.inner_text().strip()
                    else:
                        # Fallback to full text
                        full_text = suggestion.inner_text().strip()
                        # Take only first line to avoid duplicates
                        text = full_text.split('\n')[0].strip()
                except:
                    full_text = suggestion.inner_text().strip()
                    text = full_text.split('\n')[0].strip()

                # Check map icon
                has_map_icon = suggestion.locator('svg').count() > 0

                if text:  # only add if text is not empty
                    suggestion_data.append({
                        'text': text,
                        'has_map_icon': has_map_icon,
                        'index': i
                    })
                    print(f"  → '{text}' | map icon: {has_map_icon}")

            except Exception as e:
                print(f"Could not read suggestion {i}: {e}")
                continue

        assert len(suggestion_data) > 0, "Could not capture any suggestion data"

        # 13. Save to context for Step 2
        self.context['suggestion_data'] = suggestion_data
        self.context['suggestion_count'] = len(suggestion_data)

        # 14. Randomly select from successfully captured suggestions only
        selected = random.choice(suggestion_data)
        selected_index = selected['index']
        selected_text = selected['text']
        self.context['suggestion_selected'] = selected_text
        print(f"Selected suggestion: '{selected_text}'")

        # 15. Click the selected suggestion
        selected_locator = self.page.locator(
            f'#bigsearch-query-location-listbox [role="option"][data-testid="option-{selected_index}"]'
        )
        selected_locator.wait_for(state="visible", timeout=5000)
        selected_locator.click()
        self.page.wait_for_timeout(3000)
        print(f"Clicked suggestion: '{selected_text}'")
        print(f"URL after click: {self.page.url}")

        return f"Homepage loaded. Country: {country}. Suggestions: {len(suggestion_data)}. Selected: '{selected_text}'"

    def _close_popups(self):
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