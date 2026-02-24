# journey/step05_search_results.py
import random
import threading
from journey.base_step import BaseStep
from automation.models import ListingData


class Step05SearchResults(BaseStep):

    @property
    def step_number(self):
        return 5

    @property
    def test_case(self):
        return "Refine Search and Item List Verification"

    def execute(self):

        # 1. Verify on results page
        current_url = self.page.url
        assert "airbnb.com/s/" in current_url, "Not on search results page"
        print(f"Search results URL: {current_url}")

        # 2. Wait for page to load
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)

        # 3. Confirm dates and guests in URL
        assert "checkin" in current_url, "Check-in not in URL"
        assert "checkout" in current_url, "Check-out not in URL"
        assert "adults" in current_url, "Adults not in URL"
        print("Dates and guests confirmed in URL ✓")

        # 4. Wait for listing cards
        self.page.wait_for_selector(
            '[data-testid="card-container"]',
            timeout=10000
        )

        # 5. Extract listings using JavaScript (your friend's approach)
        listings = self.page.locator(
            '[data-xray-jira-component="Guest: Listing Cards"]'
        ).locator(
            '[data-testid="card-container"]'
        ).evaluate_all(
            """
            (cards) => {
                return cards.map(card => {
                    // Title
                    const titleEl = card.querySelector('[data-testid="listing-card-title"]');
                    const title = titleEl ? titleEl.innerText.trim() : "";

                    // Price
                    let price = "";
                    const priceRow = card.querySelector('[data-testid="price-availability-row"]');
                    if (priceRow) {
                        const text = priceRow.innerText;
                        const match = text.match(/\\$[\\d,]+/);
                        if (match) {
                            price = match[0];
                        }
                    }

                    // Images
                    const images = Array.from(card.querySelectorAll("picture img"))
                        .map(img => img.src)
                        .filter(Boolean);
                    const uniqueImages = [...new Set(images)];

                    return { title, price, images: uniqueImages };
                });
            }
            """
        )

        assert len(listings) > 0, "No listings found"
        print(f"Found {len(listings)} listings")

        # 6. Print and verify each listing
        for i, listing in enumerate(listings):
            image_url = listing['images'][0] if listing['images'] else "No image"
            print(f"  [{i+1}] {listing['title']} | {listing['price']} | {image_url}")

        # 7. Save to DB
        # 7. Save to DB
        def _save():
            for listing in listings:
                ListingData.objects.create(
                    journey_run=self.journey_run,
                    title=listing['title'],
                    price=listing['price'],
                    image_url=listing['images'][0] if listing['images'] else "",
                    is_selected=False
                )
        t = threading.Thread(target=_save)
        t.start()
        t.join()
        print(f"Saved {len(listings)} listings to DB")

        # 8. Save to context for Step 6
        self.context['listings'] = listings
        self.context['listing_count'] = len(listings)

        # 9. Randomly select one listing for Step 6
        selected_listing = random.choice(listings)
        self.context['selected_listing'] = selected_listing
        print(f"Selected for Step 6: '{selected_listing['title']}'")

        return f"Found and saved {len(listings)} listings. Selected: '{selected_listing['title']}'"