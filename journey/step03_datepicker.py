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

        assert checkin, "No check-in date in context"
        assert checkout, "No check-out date in context"
        assert "Available" in checkin, "Check-in date not valid"
        assert "Available" in checkout, "Check-out date not valid"

        print(f"  → Check-in: {checkin.split('.')[0]}")
        print(f"  → Check-out: {checkout.split('.')[0]}")

        return f"Dates verified. Check-in: {checkin.split('.')[0]}. Check-out: {checkout.split('.')[0]}"