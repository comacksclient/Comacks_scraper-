# """Google Maps Scraper without Email Extraction - Further Enhanced for More Results"""

# from playwright.sync_api import sync_playwright
# from dataclasses import dataclass, asdict, field
# import pandas as pd
# import argparse
# import os
# import sys
# import time
# import random

# @dataclass
# class Business:
#     name: str = None
#     address: str = None
#     website: str = None
#     phone_number: str = None
#     reviews_count: int = None
#     reviews_average: float = None

# @dataclass
# class BusinessList:
#     business_list: list[Business] = field(default_factory=list)
#     save_at = 'output'

#     def dataframe(self):
#         return pd.json_normalize(
#             (asdict(business) for business in self.business_list), sep="_"
#         )

#     def save_to_excel(self, filename):
#         if not os.path.exists(self.save_at):
#             os.makedirs(self.save_at)
#         self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

#     def save_to_csv(self, filename):
#         if not os.path.exists(self.save_at):
#             os.makedirs(self.save_at)
#         self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-s", "--search", type=str)
#     parser.add_argument("-t", "--total", type=int)
#     args = parser.parse_args()

#     if args.search:
#         search_list = [args.search]
#     else:
#         input_file_path = os.path.join(os.getcwd(), 'input.txt')
#         if os.path.exists(input_file_path):
#             with open(input_file_path, 'r') as file:
#                 search_list = [line.strip() for line in file.readlines() if line.strip()]
#         else:
#             print('Error: Pass -s search argument or create input.txt with searches')
#             sys.exit()

#     total = args.total if args.total else 1_000_000

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # Change to True for background running
#         page = browser.new_page()

#         try:
#             page.goto("https://www.google.com/maps", timeout=60000)
#             page.wait_for_timeout(5000)
#         except Exception as e:
#             print(f"Error loading Google Maps: {e}")
#             browser.close()
#             sys.exit()

#         for search_for_index, search_for in enumerate(search_list):
#             print(f"-----\n{search_for_index} - {search_for}".strip())

#             try:
#                 page.locator('//input[@id="searchboxinput"]').fill(search_for)
#                 page.wait_for_timeout(3000)
#                 page.keyboard.press("Enter")
#                 page.wait_for_timeout(10000)  # Longer initial wait for results
#             except Exception as e:
#                 print(f"Error performing search: {e}")
#                 continue

#             try:
#                 page.hover('//a[contains(@href, "https://www.google.com/maps/place")]', timeout=5000)
#             except Exception:
#                 pass

#             previously_counted = 0
#             max_scroll_attempts = 200  # Increased limit for more attempts
#             scroll_attempts = 0

#             while scroll_attempts < max_scroll_attempts:
#                 try:
#                     # Scroll gradually in bursts with random delays to mimic human behavior
#                     for _ in range(3):  # Fewer bursts but repeated
#                         page.mouse.wheel(0, random.randint(3000, 6000))
#                         time.sleep(random.uniform(1.5, 3.0))  # Randomized pause

#                     page.wait_for_timeout(6000)  # Wait for load after burst

#                     count_now = page.locator(
#                         '//a[contains(@href, "https://www.google.com/maps/place")]'
#                     ).count()

#                     print(f"Scroll attempt {scroll_attempts + 1} | Currently loaded: {count_now}")

#                     if count_now >= total:
#                         listings = page.locator(
#                             '//a[contains(@href, "https://www.google.com/maps/place")]'
#                         ).all()[:total]
#                         print(f"Reached target. Total loaded: {len(listings)}")
#                         break
#                     elif count_now == previously_counted:
#                         # Enhanced check for end of results
#                         end_indicator = page.locator('//p[contains(@class, "fontBodyMedium") and contains(text(), "reached the end") or contains(text(), "No more results")]')
#                         if end_indicator.count() > 0 or scroll_attempts > 100:
#                             listings = page.locator(
#                                 '//a[contains(@href, "https://www.google.com/maps/place")]'
#                             ).all()
#                             print(f"End of results detected. Total loaded: {len(listings)}")
#                             break
#                     previously_counted = count_now
#                     scroll_attempts += 1
#                 except Exception as e:
#                     print(f"Error during scrolling: {e}")
#                     time.sleep(5)  # Pause and retry
#                     continue

#             else:
#                 listings = page.locator(
#                     '//a[contains(@href, "https://www.google.com/maps/place")]'
#                 ).all()
#                 print(f"Max attempts reached. Total loaded: {len(listings)}")

#             business_list = BusinessList()

#             for idx, listing in enumerate(listings):
#                 try:
#                     business = Business()
#                     business.name = listing.get_attribute('aria-label') or f"Unknown_{idx}"

#                     listing.click()
#                     page.wait_for_timeout(10000)  # Longer wait for details pane

#                     address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
#                     website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
#                     phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
#                     review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
#                     reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

#                     business.address = page.locator(address_xpath).inner_text() if page.locator(address_xpath).count() > 0 else ""
#                     business.website = page.locator(website_xpath).inner_text() if page.locator(website_xpath).count() > 0 else ""
#                     business.phone_number = page.locator(phone_number_xpath).inner_text() if page.locator(phone_number_xpath).count() > 0 else ""

#                     review_text = page.locator(review_count_xpath).inner_text() if page.locator(review_count_xpath).count() > 0 else ""
#                     business.reviews_count = int(review_text.split()[0].replace('(', '').replace(')', '').replace(',', '').strip() or 0)

#                     aria_label = page.locator(reviews_average_xpath).get_attribute('aria-label') if page.locator(reviews_average_xpath).count() > 0 else ""
#                     business.reviews_average = float(aria_label.split()[0].replace(',', '.').strip() or 0.0)

#                     business_list.business_list.append(business)
#                     time.sleep(random.uniform(1, 2))  # Short pause between listings
#                 except Exception as e:
#                     print(f"Error scraping listing {idx}: {e}")
#                     continue

#             filename = f"google_maps_data_{search_for.replace(' ', '_')}"
#             business_list.save_to_excel(filename)
#             business_list.save_to_csv(filename)
#             print(f"Saved data for '{search_for}' with {len(business_list.business_list)} entries.")

#         browser.close()

# if __name__ == "__main__":
#     main()
