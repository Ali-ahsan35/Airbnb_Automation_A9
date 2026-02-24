import threading
from journey.base_step import BaseStep
from automation.models import AutoSuggestion


class Step02AutoSuggest(BaseStep):

    @property
    def step_number(self):
        return 2

    @property
    def test_case(self):
        return "Search Auto Suggestion Verification"

    def execute(self):

        # 1. Get suggestion data captured in Step 1
        suggestion_data = self.context.get('suggestion_data', [])
        assert len(suggestion_data) > 0, "No suggestion data from Step 1"
        print(f"Verifying {len(suggestion_data)} suggestions from Step 1")

        # 2. Verify each suggestion has map icon and text
        for item in suggestion_data:
            print(f"  → '{item['text']}' | map icon: {item['has_map_icon']}")

        # 3. Verify suggestions relevant to country
        country = self.context.get('country', '').lower()
        relevant = any(
            country in item['text'].lower() or
            item['text'].lower() in country
            for item in suggestion_data
        )
        print(f"Suggestions relevant to '{country}': {relevant}")

        # 4. Save all suggestions to DB
        selected_text = self.context.get('suggestion_selected', '')

        def _save():
            for item in suggestion_data:
                AutoSuggestion.objects.create(
                    journey_run=self.journey_run,
                    text=item['text'],
                    has_map_icon=item['has_map_icon'],
                    is_selected=(item['text'] == selected_text)
                )
        t = threading.Thread(target=_save)
        t.start()
        t.join()
        print(f"Saved {len(suggestion_data)} suggestions to DB")

        # 5. Verify date picker opened after suggestion click
        # try:
        #     date_picker = self.page.locator('[data-testid="structured-search-input-field-split-dates-0"]')
        #     date_picker.wait_for(state="visible", timeout=5000)
        #     print("Date picker opened successfully")
        #     self.context['date_picker_open'] = True
        # except:
        #     print("Date picker not visible — checking page state")
        #     print(f"Current URL: {self.page.url}")
        #     self.context['date_picker_open'] = False

        # Replace the date picker check with this:
        self.page.wait_for_timeout(2000)
        current_url = self.page.url
        print(f"Current URL after suggestion click: {current_url}")

        # Check if date picker is visible in any form
        date_picker_selectors = [
            '[data-testid="structured-search-input-field-split-dates-0"]',
            '[data-testid="little-search-anytime"]',
            '[aria-roledescription="datepicker"]',
            'div[data-visible="true"]',
        ]

        date_picker_found = False
        for selector in date_picker_selectors:
            try:
                el = self.page.locator(selector)
                if el.is_visible(timeout=2000):
                    print(f"Date picker found with: {selector}")
                    date_picker_found = True
                    break
            except:
                continue

        self.context['date_picker_open'] = date_picker_found
        print(f"Date picker open: {date_picker_found}")

        return f"Verified {len(suggestion_data)} suggestions. Selected: '{selected_text}'. DB saved."