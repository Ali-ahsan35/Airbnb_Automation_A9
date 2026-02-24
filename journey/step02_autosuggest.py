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
        suggestion_data = self.context.get('suggestion_data', [])
        assert len(suggestion_data) > 0, "No suggestion data from Step 1"

        country = self.context.get('country', '').lower()
        relevant = any(
            country in item['text'].lower() or
            item['text'].lower() in country
            for item in suggestion_data
        )
        print(f"  → {len(suggestion_data)} suggestions verified | Relevant: {relevant}")

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

        try:
            date_picker = self.page.locator(
                '[data-testid="structured-search-input-field-split-dates-0"]'
            )
            date_picker.wait_for(state="visible", timeout=5000)
            self.context['date_picker_open'] = True
        except:
            self.context['date_picker_open'] = False

        return f"Verified {len(suggestion_data)} suggestions. Selected: '{selected_text}'"