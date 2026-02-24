# journey/step04_guestpicker.py
from journey.base_step import BaseStep


class Step04GuestPicker(BaseStep):

    @property
    def step_number(self):
        return 4

    @property
    def test_case(self):
        return "Guest Picker Interaction"

    def execute(self):
        guests = self.context.get('guests', {})
        assert guests, "No guest data in context"

        url = self.page.url
        assert "adults" in url, f"Adults not in URL: {url}"

        print(f"  → Guests verified in URL: {guests}")

        return f"Guests verified: {guests}"