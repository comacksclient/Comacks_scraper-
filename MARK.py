"""Website Scraper for Business Names, Doctor Names, and Emails"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

# Extract all emails from a single page
def get_emails_from_page(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return []
        content = response.text
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)
        return list(set(emails))  # Remove duplicates
    except Exception:
        return []  # Silently handle errors to make it error-free

# Extract likely doctor names only
def get_doctor_names_from_page(url):
    doctor_names = set()
    exclude_words = {
        "Dental", "Dentist", "Office", "Implants", "Crowns", "Veneers", "Invisalign",
        "Family", "Pediatric", "Emergency", "Cosmetic", "Patient", "Information", "Teeth",
        "Whitening", "United", "States", "Friendly", "Local", "Long", "Island", "New", "York"
    }

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return doctor_names
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        patterns = [
            r"Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+",       # Dr. John Smith
            r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+,\s*(?:DDS|DMD)"  # John Smith, DDS/DMD
        ]

        for pattern in patterns:
            for match in re.findall(pattern, text):
                if not any(word in match for word in exclude_words):
                    doctor_names.add(match.strip())

        return doctor_names
    except Exception:
        return doctor_names  # Silently handle errors

# Extract business name from the homepage (e.g., from <title> or <h1>)
def get_business_name_from_page(url, soup=None):
    try:
        if not soup:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                return ""
            soup = BeautifulSoup(response.text, "html.parser")
        
        # Try <title> tag
        title = soup.title.string.strip() if soup.title else ""
        if title:
            # Clean up common suffixes
            for suffix in [" | Dental Clinic", " - Dentist", " | Home", " - Your Dental Care"]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            return title
        
        # Fallback to first <h1>
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else ""
    except Exception:
        return ""

# Main scraping function for one website
def scrape_dental_site(base_url):
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme:
        base_url = "https://" + base_url

    subpages = ["", "contact", "about", "team", "staff", "our-team", "meet-the-team"]

    all_emails = set()
    all_doctors = set()
    business_name = ""

    # First, get business name from homepage
    homepage = urljoin(base_url, "")
    try:
        response = requests.get(homepage, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            business_name = get_business_name_from_page(homepage, soup)
    except Exception:
        pass  # Continue with fallback

    # Scrape subpages for emails and doctors
    for sub in subpages:
        full_url = urljoin(base_url, sub)
        all_emails.update(get_emails_from_page(full_url))
        all_doctors.update(get_doctor_names_from_page(full_url))

    # If no business name found, use domain as fallback
    if not business_name:
        business_name = parsed_url.netloc.replace("www.", "")

    return {
        'business_name': business_name,
        'doctor': ', '.join(sorted(all_doctors)) if all_doctors else '',
        'email': ', '.join(sorted(all_emails)) if all_emails else ''
    }

if __name__ == "__main__":
    input_file = "websites.txt"
    output_csv = "scraped_data.csv"

    try:
        with open(input_file, "r") as file:
            websites = [line.strip() for line in file if line.strip()]
        if not websites:
            print("Warning: 'websites.txt' is empty. No data to scrape.")
            exit()
    except FileNotFoundError:
        print("Error: 'websites.txt' not found. Please create it with one website URL per line.")
        exit()
    except Exception:
        print("Error: Failed to read 'websites.txt'. Ensure it's a valid text file.")
        exit()

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(scrape_dental_site, websites))

    # Create output DataFrame and save to CSV
    if results:
        output_df = pd.DataFrame(results)
        output_df.to_csv(output_csv, index=False)
        print(f"Success: Saved results to {output_csv} with {len(output_df)} entries.")
    else:
        print("No results to save.")
