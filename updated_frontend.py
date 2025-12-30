import os
import httpx
import json
import re
import io
import csv
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_BASE = "https://google.serper.dev"

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
FACEBOOK_HOST = "facebook-scraper3.p.rapidapi.com"
INSTAGRAM_HOST = "instagram-scraper-stable-api.p.rapidapi.com"
FACEBOOK_API_BASE = f"https://{FACEBOOK_HOST}"
INSTAGRAM_API_BASE = f"https://{INSTAGRAM_HOST}"

def fetch_google_search(query: str, gl: str = "in", num: int = 10, page: int = 1):
    payload = {
        "q": query,
        "gl": gl,
        "num": num,
        "page": page
    }
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{SERPER_API_BASE}/search",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Error fetching Google search data: {e}")
        return None

def extract_social_url(data, domain):
    if not data:
        return ""
    organic = data.get("organic", [])
    for item in organic:
        for field in ["link", "snippet", "title"]:
            text = str((item or {}).get(field, ""))
            if domain in text.lower():
                words = text.split()
                for word in words:
                    if word.startswith("http") and domain in word.lower():
                        return word.rstrip('.,;)')
                if text.startswith("http") and domain in text.lower():
                    return text.rstrip('.,;)')
    full_text = json.dumps(data).lower()
    if domain in full_text:
        pattern = rf'https?://[^\s"\'>]*{domain}[^\s"\'>]*'
        match = re.search(pattern, full_text)
        if match:
            return match.group()
    return ""

def get_clinic_socials(clinic_name: str):
    query = f'"{clinic_name}" contact'
    data = fetch_google_search(query, gl="in", num=10, page=1)
    facebook_url = extract_social_url(data, "facebook.com")
    instagram_url = extract_social_url(data, "instagram.com")
    return {
        "clinic_name": clinic_name,
        "facebook_url": facebook_url,
        "instagram_url": instagram_url
    }

def fetch_facebook_profile(profile_url: str):
    params = {"url": profile_url}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": FACEBOOK_HOST
    }
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{FACEBOOK_API_BASE}/profile/details_url",
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Error fetching Facebook profile: {e}")
        return None

def get_facebook_profile_dict(profile_url: str):
    data = fetch_facebook_profile(profile_url)
    result = {
        "name": "", "profile_url": profile_url, "profile_image": "", "cover_image": "",
        "description": "", "address": "", "phone": "", "website": "", "instagram": ""
    }
    profile = (data or {}).get("profile", {})
    result["name"] = profile.get("name", "")
    result["profile_image"] = profile.get("image", "")
    result["cover_image"] = profile.get("cover_image", "")
    result["description"] = profile.get("intro", "")
    for item in profile.get("about_public", []):
        text = (item.get("text") or "").strip()
        url = (item.get("external_url") or "").strip()
        if re.search(r"\+?\d[\d\s-]{7,}", text):
            result["phone"] = text
        elif re.search(r"Bhawani Singh lane|Scheme|Jaipur", text, re.I):
            result["address"] = text
        elif url and "instagram.com" in url:
            result["instagram"] = url
        elif ("com" in text and url) or (url and url.startswith("http")):
            result["website"] = url
    return result

def fetch_instagram_profile(instagram_url_or_username: str):
    params = {"username_or_url": instagram_url_or_username}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": INSTAGRAM_HOST
    }
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{INSTAGRAM_API_BASE}/ig_get_fb_profile_hover.php",
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Error fetching Instagram profile: {e}")
        return None

def get_instagram_profile_dict(instagram_url_or_username: str):
    data = fetch_instagram_profile(instagram_url_or_username)
    result = {
        "name": data.get("username", "") or data.get("name", ""),
        "profile_url": data.get("url", "") or instagram_url_or_username,
        "profile_image": data.get("profile_pic_url", ""),
        "cover_image": "",
        "description": data.get("bio", ""),
        "address": "",
        "phone": "",
        "website": data.get("website", ""),
        "instagram": data.get("url", "") or instagram_url_or_username
    }
    return result

st.title("Bulk Clinic Social Media Finder")
tab1, tab2 = st.tabs(["Bulk Clinic Name to Social URLs", "Bulk Facebook/Instagram URL Info"])
with tab1:
    clinic_names_input = st.text_area("Enter clinic names (one per line):", height=300)
    if st.button("Find Social URLs for All Clinics"):
        names = [name.strip() for name in clinic_names_input.splitlines() if name.strip()]
        if not names:
            st.warning("Please enter at least one clinic name, one per line.")
        else:
            results = []
            progress = st.progress(0)
            total = len(names)
            with st.spinner(f"Searching for {total} clinic(s)..."):
                for idx, clinic_name in enumerate(names, 1):
                    result = get_clinic_socials(clinic_name)
                    results.append(result)
                    progress.progress(idx / total)
            st.success(f"Search completed for {total} clinic(s)!")
            
            # Display results table
            st.dataframe(results)
            
            # CSV download
            csv_content = "clinic_name,facebook_url,instagram_url\n"
            for row in results:
                values = [row["clinic_name"], row["facebook_url"], row["instagram_url"]]
                csv_content += ",".join([f'"{v}"' for v in values]) + "\n"
            st.download_button(
                label="Download CSV for All Clinics",
                data=csv_content,
                file_name="clinic_socials.csv",
                mime="text/csv"
            )
with tab2:
    st.subheader("Bulk Facebook/Instagram URL Info Scraper")
    urls_input = st.text_area("Paste Facebook or Instagram URLs/usernames (one per line):", height=200)
    scrape_type = st.radio("Choose Type", options=["Facebook", "Instagram"])
    if st.button("Scrape Profiles"):
        urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
        if not urls:
            st.warning("Enter one or more Facebook/Instagram URLs or usernames.")
        else:
            results = []
            progress = st.progress(0)
            for idx, url in enumerate(urls, 1):
                if scrape_type == "Facebook":
                    row = get_facebook_profile_dict(url)
                else:
                    row = get_instagram_profile_dict(url)
                results.append(row)
                progress.progress(idx / len(urls) if urls else 1)
            st.dataframe(results)
            # Prepare the CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "name", "profile_url", "profile_image", "cover_image", "description",
                "address", "phone", "website", "instagram"
            ])
            writer.writeheader()
            for row in results:
                writer.writerow(row)
            st.download_button(
                label="Download CSV",
                data=output.getvalue(),
                file_name=f"{scrape_type.lower()}_profiles.csv",
                mime="text/csv"
            )
