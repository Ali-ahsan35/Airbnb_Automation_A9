# journey/step03_datepicker.py
import threading
from journey.base_step import BaseStep


class Step03DatePicker(BaseStep):

    @property
    def step_number(self):
        return 3

    @property
    def test_case(self):
        return "Date Picker Interaction"

    def execute(self):

        checkin = self.context.get('checkin', '')
        checkout = self.context.get('checkout', '')
        next_month_clicks = self.context.get('next_month_clicks', 0)

        assert checkin, "No check-in date in context"
        assert checkout, "No check-out date in context"

        print(f"Check-in: {checkin}")
        print(f"Check-out: {checkout}")
        print(f"Next month clicks: {next_month_clicks}")
        print(f"Current URL: {self.page.url}")

        # Verify dates appear in URL
        url = self.page.url
        assert "checkin" in url, f"Check-in not in URL: {url}"
        assert "checkout" in url, f"Check-out not in URL: {url}"
        print("Dates verified in URL ✓")

        return f"Dates verified. Check-in: {checkin}. Check-out: {checkout}"