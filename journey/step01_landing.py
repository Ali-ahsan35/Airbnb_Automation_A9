# journey/step01_landing.py
import random
import re
from journey.base_step import BaseStep


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

        # ── STEP 1 LOGIC: Location ──────────────────────────────

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
        self.page.wait_for_timeout(2000)
        print("Suggestions visible")

        # 11. Capture all suggestions
        suggestions = self.page.locator(
            '#bigsearch-query-location-listbox [role="option"]'
        ).all()
        assert len(suggestions) > 0, "No suggestions found"
        print(f"Found {len(suggestions)} suggestions")

        suggestion_data = []
        for i, suggestion in enumerate(suggestions):
            try:
                suggestion.wait_for(state="visible", timeout=5000)
                try:
                    text_div = suggestion.locator('div[class*="t5i37sl"]')
                    if text_div.count() > 0:
                        text = text_div.first.inner_text().strip()
                    else:
                        full_text = suggestion.inner_text().strip()
                        text = full_text.split('\n')[0].strip()
                except:
                    full_text = suggestion.inner_text().strip()
                    text = full_text.split('\n')[0].strip()

                has_map_icon = suggestion.locator('svg').count() > 0
                if text:
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
        self.context['suggestion_data'] = suggestion_data

        # 12. Click random suggestion
        selected = random.choice(suggestion_data)
        selected_index = selected['index']
        selected_text = selected['text']
        self.context['suggestion_selected'] = selected_text
        print(f"Selected suggestion: '{selected_text}'")

        selected_locator = self.page.locator(
            f'#bigsearch-query-location-listbox [role="option"][data-testid="option-{selected_index}"]'
        )
        selected_locator.wait_for(state="visible", timeout=5000)
        selected_locator.click()
        self.page.wait_for_timeout(2000)
        print(f"Clicked suggestion: '{selected_text}'")

        # ── STEP 3 LOGIC: Date Picker ───────────────────────────

        # 13. Click date field to open date picker
        try:
            date_field = self.page.get_by_test_id(
                "structured-search-input-field-split-dates-0"
            )
            date_field.wait_for(state="visible", timeout=5000)
            date_field.click()
            self.page.wait_for_timeout(1000)
            print("Date picker opened")
        except:
            print("Date picker may already be open")

        # 14. Click Next Month randomly 3-8 times
        next_month_clicks = random.randint(3, 8)
        print(f"Clicking next month {next_month_clicks} times")

        for i in range(next_month_clicks):
            try:
                next_btn = self.page.get_by_role(
                    "button",
                    name=re.compile(r"Move forward to switch to the")
                )
                next_btn.wait_for(state="visible", timeout=5000)
                next_btn.click()
                self.page.wait_for_timeout(500)
                print(f"  Next month click {i+1}/{next_month_clicks}")
            except Exception as e:
                print(f"  Could not click next month: {e}")
                break

        self.page.wait_for_timeout(1000)

        # 15. Get available dates

        self.page.wait_for_timeout(1000)
        available_dates = self.page.locator(
            'button[aria-label*="Available. Select as check-in date"]'
        ).all()
        assert len(available_dates) >= 2, "Not enough available dates"
        print(f"Found {len(available_dates)} available dates")

        # 16. Pick check-in from first half
        checkin_index = random.randint(0, len(available_dates) // 2 - 1)
        checkin_btn = available_dates[checkin_index]
        checkin_label = checkin_btn.get_attribute("aria-label")
        print(f"Check-in selected: {checkin_label}")
        checkin_btn.click()
        self.page.wait_for_timeout(1500)

        # 17. NOW get checkout dates — list changes after check-in click
        # Airbnb shows "Select as checkout date" labels after check-in is picked
        checkout_dates = self.page.locator(
            'button[aria-label*="Available. Select as checkout date"]'
        ).all()

        # Fallback if checkout-specific label not found
        if len(checkout_dates) == 0:
            print("No checkout-specific dates found, using all available")
            checkout_dates = self.page.locator(
                'button[aria-label*="Available"]'
            ).all()

        assert len(checkout_dates) >= 1, "No checkout dates available"
        print(f"Found {len(checkout_dates)} checkout dates")

        # Pick checkout 1-14 days after check-in
        max_offset = min(14, len(checkout_dates) - 1)
        offset = random.randint(1, max(1, max_offset))
        checkout_index = min(offset, len(checkout_dates) - 1)
        checkout_btn = checkout_dates[checkout_index]
        checkout_label = checkout_btn.get_attribute("aria-label")
        print(f"Check-out selected: {checkout_label}")
        checkout_btn.click()
        self.page.wait_for_timeout(1500)

        # 18. Save to context — done, do NOT click any more dates
        self.context['checkin'] = checkin_label
        self.context['checkout'] = checkout_label
        self.context['next_month_clicks'] = next_month_clicks
        print("Date selection complete ✓")

        # ── STEP 4 LOGIC: Guests ────────────────────────────────

        # 18. Click guests field
        try:
            guest_field = self.page.get_by_role("button", name="Who Add guests")
            guest_field.wait_for(state="visible", timeout=5000)
            guest_field.click()
            self.page.wait_for_timeout(1000)
            print("Guest picker opened")
        except:
            guest_field = self.page.get_by_test_id(
                "structured-search-input-field-guests-button"
            )
            guest_field.click()
            self.page.wait_for_timeout(1000)

        # 19. Select random guests
        guests = {
            'adults': random.randint(1, 3),
            'children': random.randint(0, 2),
            'infants': random.randint(0, 2),
            'pets': random.randint(0, 1),
        }
        print(f"Adding guests: {guests}")

        for _ in range(guests['adults']):
            self.page.get_by_test_id("stepper-adults-increase-button").click()
            self.page.wait_for_timeout(300)

        for _ in range(guests['children']):
            self.page.get_by_test_id("stepper-children-increase-button").click()
            self.page.wait_for_timeout(300)

        for _ in range(guests['infants']):
            self.page.get_by_test_id("stepper-infants-increase-button").click()
            self.page.wait_for_timeout(300)

        for _ in range(guests['pets']):
            self.page.get_by_test_id("stepper-pets-increase-button").click()
            self.page.wait_for_timeout(300)

        self.context['guests'] = guests
        self.context['total_guests'] = guests['adults'] + guests['children']
        print(f"Guests added: {guests}")

        # 20. Click Search button
        search_btn = self.page.get_by_test_id(
            "structured-search-input-search-button"
        )
        search_btn.wait_for(state="visible", timeout=5000)
        search_btn.click()
        self.page.wait_for_timeout(3000)
        print(f"Search clicked. URL: {self.page.url}")

        assert "airbnb.com/s/" in self.page.url, \
            f"Search did not navigate. URL: {self.page.url}"

        return (
            f"Country: {country} | "
            f"Suggestion: {selected_text} | "
            f"Check-in: {checkin_label} | "
            f"Check-out: {checkout_label} | "
            f"Guests: {guests}"
        )

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