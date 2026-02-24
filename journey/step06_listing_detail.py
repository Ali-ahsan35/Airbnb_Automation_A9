# journey/step06_listing_detail.py
import threading
from journey.base_step import BaseStep
from automation.models import ListingDetail


class Step06ListingDetail(BaseStep):

    @property
    def step_number(self):
        return 6

    @property
    def test_case(self):
        return "Item Details Page Verification"

    def execute(self):

        # 1. Get selected listing from context
        selected_listing = self.context.get('selected_listing', {})
        selected_title = selected_listing.get('title', '')
        assert selected_title, "No listing selected from Step 5"
        print(f"Looking for listing: '{selected_title}'")

        # 2. Find the anchor tag that wraps the listing card
        # The anchor has aria-labelledby pointing to the title
        listing_link = self.page.locator(
            f'a[aria-labelledby*="title_"]'
        ).filter(
            has=self.page.locator(f'[data-testid="listing-card-title"]').filter(has_text=selected_title)
        ).first

        try:
            listing_link.wait_for(state="visible", timeout=5000)

            # Get the href before clicking
            href = listing_link.get_attribute("href")
            print(f"Found listing href: {href[:80]}...")

            # Open in same page by navigating directly
            if href:
                if href.startswith("/"):
                    href = f"https://www.airbnb.com{href}"
                
                # Use new tab approach since Airbnb opens in new tab
                with self.page.context.expect_page() as new_page_info:
                    listing_link.click()
                new_page = new_page_info.value
                new_page.wait_for_load_state("domcontentloaded")
                self.page = new_page
                print("Opened in new tab")
            
        except Exception as e:
            print(f"Link click failed: {e}, trying direct navigation")
            # Fallback — navigate directly using href
            listing_link2 = self.page.locator(
                'a[aria-labelledby*="title_"]'
            ).first
            href = listing_link2.get_attribute("href")
            if href and href.startswith("/"):
                href = f"https://www.airbnb.com{href}"
            self.page.goto(href)
            self.page.wait_for_load_state("domcontentloaded")

        self.page.wait_for_timeout(3000)
        current_url = self.page.url
        print(f"Detail page URL: {current_url}")

        # 3. Capture title
        try:
            title = self.page.locator(
                '[data-section-id="TITLE_DEFAULT"] h1'
            ).first.inner_text().strip()
        except:
            try:
                title = self.page.locator('h1').first.inner_text().strip()
            except:
                title = selected_title
        print(f"Title: '{title}'")

        # 4. Capture subtitle
        try:
            subtitle = self.page.locator(
                '[data-section-id="TITLE_DEFAULT"] h2'
            ).first.inner_text().strip()
        except:
            try:
                subtitle = self.page.locator('h2').first.inner_text().strip()
            except:
                subtitle = ""
        print(f"Subtitle: '{subtitle}'")

        # 5. Collect ALL image URLs
        image_urls = self.page.evaluate("""
            () => {
                const images = Array.from(
                    document.querySelectorAll('picture img, img[src*="muscache"]')
                );
                const urls = images
                    .map(img => img.src)
                    .filter(url => url && url.includes('muscache'));
                return [...new Set(urls)];
            }
        """)
        print(f"Found {len(image_urls)} images")
        for url in image_urls[:3]:
            print(f"  → {url[:80]}...")

        # 6. Save to DB
        def _save():
            ListingDetail.objects.create(
                journey_run=self.journey_run,
                title=title,
                subtitle=subtitle,
                image_urls=image_urls,
                page_url=current_url
            )
        t = threading.Thread(target=_save)
        t.start()
        t.join()
        print("Listing detail saved to DB ✓")

        return (
            f"Title: '{title}' | "
            f"Subtitle: '{subtitle}' | "
            f"Images: {len(image_urls)} | "
            f"URL: {current_url}"
        )