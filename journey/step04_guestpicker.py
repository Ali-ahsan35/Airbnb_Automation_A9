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
        total = self.context.get('total_guests', 0)

        assert guests, "No guest data in context"
        print(f"Guests: {guests}")
        print(f"Total: {total}")

        # Verify guests in URL
        url = self.page.url
        assert "adults" in url, f"Adults not in URL: {url}"
        print("Guests verified in URL ✓")
        print(f"Current URL: {url}")

        return f"Guests verified. {guests}. URL: {url}"