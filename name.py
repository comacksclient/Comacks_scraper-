# # use thsis for name and email extraction 

# import requests
# from bs4 import BeautifulSoup
# import re
# from urllib.parse import urljoin, urlparse
# from concurrent.futures import ThreadPoolExecutor

# # Extract all emails from a single page
# def get_emails_from_page(url):
#     try:
#         response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
#         if response.status_code != 200:
#             return []
#         content = response.text
#         emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)
#         return list(set(emails))
#     except Exception as e:
#         print(f"[ERROR] Failed to scrape {url} — {e}")
#         return []

# # Extract likely doctor names only
# def get_doctor_names_from_page(url):
#     doctor_names = set()
#     exclude_words = {
#         "Dental", "Dentist", "Office", "Implants", "Crowns", "Veneers", "Invisalign",
#         "Family", "Pediatric", "Emergency", "Cosmetic", "Patient", "Information", "Teeth",
#         "Whitening", "United", "States", "Friendly", "Local", "Long", "Island", "New", "York"
#     }

#     try:
#         response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
#         if response.status_code != 200:
#             return doctor_names
#         soup = BeautifulSoup(response.text, "html.parser")
#         text = soup.get_text(separator=" ", strip=True)

#         patterns = [
#             r"Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+",       # Dr. John Smith
#             r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+,\s*(?:DDS|DMD)"  # John Smith, DDS/DMD
#         ]

#         for pattern in patterns:
#             for match in re.findall(pattern, text):
#                 if not any(word in match for word in exclude_words):
#                     doctor_names.add(match.strip())

#         return doctor_names
#     except Exception as e:
#         print(f"[ERROR] Failed to scrape doctor names from {url} — {e}")
#         return doctor_names

# # Main scraping function for one website
# def scrape_dental_site(base_url):
#     parsed_url = urlparse(base_url)
#     if not parsed_url.scheme:
#         base_url = "https://" + base_url

#     subpages = ["", "contact", "about", "team", "staff", "our-team", "meet-the-team"]

#     all_emails = set()
#     all_doctors = set()

#     for sub in subpages:
#         full_url = urljoin(base_url, sub)
#         print(f"[INFO] Checking {full_url} ...")
#         all_emails.update(get_emails_from_page(full_url))
#         all_doctors.update(get_doctor_names_from_page(full_url))

#     return all_emails, all_doctors

# if __name__ == "__main__":
#     try:
#         with open("websites.txt", "r") as file:
#             websites = [line.strip() for line in file if line.strip()]
#     except FileNotFoundError:
#         print("[ERROR] 'websites.txt' file not found. Please create it with one URL per line.")
#         exit()

#     all_emails_global = set()
#     all_doctors_global = set()

#     with ThreadPoolExecutor(max_workers=10) as executor:
#         results = executor.map(scrape_dental_site, websites)

#         for emails, doctors in results:
#             all_emails_global.update(emails)
#             all_doctors_global.update(doctors)

#     # Save emails
#     if all_emails_global:
#         with open("emails.txt", "w") as f:
#             for email in sorted(all_emails_global):
#                 f.write(email + "\n")
#         print(f"[SUCCESS] Saved {len(all_emails_global)} unique emails to emails.txt")
#     else:
#         print("[INFO] No emails found.")

#     # Save doctors
#     if all_doctors_global:
#         with open("doctors.txt", "w") as f:
#             for doctor in sorted(all_doctors_global):
#                 f.write(doctor + "\n")
#         print(f"[SUCCESS] Saved {len(all_doctors_global)} doctor names to doctors.txt")
#     else:
#         print("[INFO] No doctor names found.")
