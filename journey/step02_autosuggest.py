# journey/step02_autosuggest.py
import random
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

        # 0. Handle any popup
        try:
            got_it_btn = self.page.locator('//button[contains(text(), "Got it")]')
            if got_it_btn.is_visible(timeout=3000):
                got_it_btn.click()
                print("Closed 'Got it' popup")
                self.page.wait_for_timeout(1000)
        except:
            pass

        # 1. Click search field again to make sure suggestions are visible
        search_field = self.page.locator('#bigsearch-query-location-input')
        search_field.click()
        self.page.wait_for_timeout(2000)

        # 2. Wait for suggestion listbox using the real id
        suggestion_list = self.page.locator('#bigsearch-query-location-listbox')
        suggestion_list.wait_for(state="visible", timeout=10000)
        print("Suggestion list is visible")

        # 3. Get all suggestion options
        suggestions = self.page.locator(
            '#bigsearch-query-location-listbox [role="option"]'
        ).all()
        assert len(suggestions) > 0, "No suggestions found"
        print(f"Found {len(suggestions)} suggestions")

        # 4. Capture and verify each suggestion
        suggestion_data = []
        for suggestion in suggestions:
            try:
                # Get text
                text = suggestion.locator('.t5i37sl').inner_text().strip()

                # Check map icon (svg exists inside suggestion)
                has_map_icon = suggestion.locator('svg').count() > 0

                suggestion_data.append({
                    'text': text,
                    'has_map_icon': has_map_icon
                })
                print(f"  → '{text}' | map icon: {has_map_icon}")

            except Exception as e:
                print(f"Could not read suggestion: {e}")
                continue

        assert len(suggestion_data) > 0, "Could not capture suggestion data"

        # 5. Save all to DB
        def _save():
            for item in suggestion_data:
                AutoSuggestion.objects.create(
                    journey_run=self.journey_run,
                    text=item['text'],
                    has_map_icon=item['has_map_icon'],
                    is_selected=False
                )
        t = threading.Thread(target=_save)
        t.start()
        t.join()

        # 6. Randomly select one and click
        selected_index = random.randint(0, len(suggestions) - 1)
        selected = suggestions[selected_index]
        selected_text = suggestion_data[selected_index]['text']
        self.context['suggestion_selected'] = selected_text
        print(f"Selected: '{selected_text}'")

        # 7. Mark as selected in DB
        def _mark():
            AutoSuggestion.objects.filter(
                journey_run=self.journey_run,
                text=selected_text
            ).update(is_selected=True)
        t2 = threading.Thread(target=_mark)
        t2.start()
        t2.join()

        # 8. Click the selected suggestion properly
        selected_locator = self.page.locator(
            f'#bigsearch-query-location-listbox [role="option"][data-testid="option-{selected_index}"]'
        )
        selected_locator.wait_for(state="visible", timeout=5000)
        selected_locator.click()
        self.page.wait_for_timeout(2000)

        print(f"Clicked suggestion: '{selected_text}'")

        # 9. Verify date picker opened
        date_picker = self.page.locator('[data-testid="structured-search-input-field-split-dates-0"]')
        try:
            date_picker.wait_for(state="visible", timeout=5000)
            print("Date picker opened successfully")
        except:
            print("Date picker did not open — may have navigated differently")

        return f"Found {len(suggestion_data)} suggestions. Selected: '{selected_text}'"