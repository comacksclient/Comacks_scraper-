## Do not use this file -> not for use 
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

def get_emails_from_page(url):
    """Fetch a page and extract all email addresses."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return []
        content = response.text
        # Regex to find emails
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)
        return list(set(emails))
    except Exception as e:
        print(f"[ERROR] Failed to scrape {url} — {e}")
        return []

def scrape_dental_site(base_url):
    """Scrape emails from homepage and important subpages."""
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme:
        base_url = "https://" + base_url

    # Pages to check
    subpages = ["", "contact", "about", "team", "staff", "our-team", "meet-the-team"]

    all_emails = set()
    for sub in subpages:
        full_url = urljoin(base_url, sub)
        print(f"[INFO] Checking {full_url} ...")
        emails = get_emails_from_page(full_url)
        all_emails.update(emails)

    # Save to file
    if all_emails:
        with open("emails.txt", "w") as f:
            for email in sorted(all_emails):
                f.write(email + "\n")
        print(f"[SUCCESS] Found {len(all_emails)} emails. Saved to emails.txt")
    else:
        print("[INFO] No emails found.")

if __name__ == "__main__":
    # Example — Replace with your dental clinic URL
    website_link = input("Enter dental clinic website URL: ").strip()
    scrape_dental_site(website_link)
