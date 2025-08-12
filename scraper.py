# use this as the main file

"""Google Maps Scraper without Email Extraction"""

from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None

@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)
    save_at = 'output'

    def dataframe(self):
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    def save_to_excel(self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()

    if args.search:
        search_list = [args.search]
    else:
        input_file_path = os.path.join(os.getcwd(), 'input.txt')
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r') as file:
                search_list = [line.strip() for line in file.readlines() if line.strip()]
        else:
            print('Error: Pass -s search argument or create input.txt with searches')
            sys.exit()

    total = args.total if args.total else 1_000_000

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(5000)

        for search_for_index, search_for in enumerate(search_list):
            print(f"-----\n{search_for_index} - {search_for}".strip())

            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)

            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(3000)

                count_now = page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).count()

                if count_now >= total:
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()[:total]
                    print(f"Total Scraped: {len(listings)}")
                    break
                elif count_now == previously_counted:
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()
                    print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                    break
                else:
                    previously_counted = count_now
                    print(f"Currently Scraped: {count_now}")

            business_list = BusinessList()

            for listing in listings:
                try:
                    business = Business()

                    business.name = listing.get_attribute('aria-label') or ""

                    listing.click()
                    page.wait_for_timeout(5000)

                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                    review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                    business.address = page.locator(address_xpath).all()[0].inner_text() if page.locator(address_xpath).count() > 0 else ""
                    business.website = page.locator(website_xpath).all()[0].inner_text() if page.locator(website_xpath).count() > 0 else ""
                    business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text() if page.locator(phone_number_xpath).count() > 0 else ""

                    if page.locator(review_count_xpath).count() > 0:
                        business.reviews_count = int(
                            page.locator(review_count_xpath).inner_text().split()[0].replace(',', '').strip()
                        )
                    else:
                        business.reviews_count = ""

                    if page.locator(reviews_average_xpath).count() > 0:
                        business.reviews_average = float(
                            page.locator(reviews_average_xpath).get_attribute('aria-label').split()[0].replace(',', '.').strip()
                        )
                    else:
                        business.reviews_average = ""

                    business_list.business_list.append(business)

                except Exception as e:
                    print(f"Error occurred: {e}")

            filename = f"google_maps_data_{search_for}".replace(' ', '_')
            business_list.save_to_excel(filename)
            business_list.save_to_csv(filename)

        browser.close()

if __name__ == "__main__":
    main()
