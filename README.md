# Maps Website Scraper Project
<important files :::: ------ >>>>> MARK.py { is for websote scraping } 
scraper.py -> is for maps scraping 

for the socials use updated_frontend.py  and updated_frontend2.py

A comprehensive web scraping toolkit for extracting business information from Google Maps and websites. This project includes multiple scrapers for gathering business details, contact information, doctor names, and social media profiles.

## Project Overview

This project consists of three main components:

1. **Google Maps Scraper** (`scraper.py`) - Extracts business listings from Google Maps
2. **Website Scraper** (`MARK.py`) - Scrapes websites for emails, doctor names, and business information
3. **Social Media Scraper** (`socials-scraper/`) - Finds and analyzes social media profiles using Streamlit UI

## Project Structure

```
maps-website scraper/
├── scraper.py                    # Google Maps scraper (main scraper)
├── MARK.py                       # Website scraper for emails and doctor names
├── requirements.txt              # Python dependencies
├── websites.txt                  # Input file: list of websites to scrape
├── emails.txt                    # Output: extracted emails
├── output/                       # Output directory for Excel/CSV files
└── socials-scraper/
    ├── updated_frontend.py       # Streamlit UI for social media scraping
    ├── updated_frontend2.py      # Alternative Streamlit UI version
    └── env                       # Virtual environment directory
```

## Features

### 1. Google Maps Scraper (`scraper.py`)
- Searches for businesses on Google Maps
- Extracts business information:
  - Business name
  - Address
  - Website URL
  - Phone number
  - Review count
  - Average rating
- Outputs results in both Excel (.xlsx) and CSV (.csv) formats
- Supports batch searching from input file or command-line arguments

### 2. Website Scraper (`MARK.py`)
- Scrapes dental/medical websites (customizable for any type)
- Extracts:
  - Business/Practice name
  - Doctor names (with pattern recognition)
  - Email addresses (from multiple pages)
- Searches common pages: homepage, contact, about, team, staff, our-team, meet-the-team
- Parallel processing for faster scraping (up to 10 concurrent requests)
- Outputs results to CSV file

### 3. Social Media Scraper (`socials-scraper/`)
- Streamlit-based web UI
- Integrates with:
  - Google Search (via Serper API)
  - Facebook (via RapidAPI)
  - Instagram (via RapidAPI)
- Searches for social media profiles
- Extracts social media insights and analytics

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Installation

#### 1. Clone or navigate to the project directory
```bash
cd /Users/arpitgupta/Desktop/comacks/maps-website\ scraper\ 
```

#### 2. Create a virtual environment (optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install additional dependencies for Playwright (if using Google Maps Scraper)
```bash
playwright install
```

## Usage Guide

### Running the Google Maps Scraper

#### Option A: Search from command line
```bash
python scraper.py -s "dentist in New York" -t 100
```

Parameters:
- `-s, --search`: Search query (e.g., "dentist in New York")
- `-t, --total`: Maximum number of results to scrape (default: 1,000,000)

Example:
```bash
python scraper.py -s "restaurants in London" -t 50
```

#### Option B: Search from input file
1. Create a file named `input.txt` in the project root
2. Add one search query per line:
   ```
   dentist in New York
   doctor in Los Angeles
   restaurant in Chicago
   ```
3. Run the scraper:
   ```bash
   python scraper.py
   ```

**Output:** 
- Excel file: `output/google_maps_data_<search_term>.xlsx`
- CSV file: `output/google_maps_data_<search_term>.csv`

### Running the Website Scraper

#### 1. Prepare websites list
Create a `websites.txt` file with URLs (one per line):
```
https://www.oldglory.in/
https://www.newyorkdentaloffice.com/
https://example-dental.com/
```

#### 2. Run the scraper
```bash
python MARK.py
```

**Output:** 
- CSV file: `scraped_data.csv` with columns:
  - `business_name`: Name of the practice/business
  - `doctor`: Extracted doctor names
  - `email`: Extracted email addresses

### Running the Social Media Scraper

#### 1. Setup environment variables
Create a `.env` file in the `socials-scraper` directory:
```
SERPER_API_KEY=your_serper_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
```

Get API keys:
- **Serper API**: https://serper.dev/
- **RapidAPI**: https://rapidapi.com/

#### 2. Install Streamlit (if not already installed)
```bash
pip install streamlit
```

#### 3. Run the Streamlit app
Navigate to the socials-scraper directory:
```bash
cd socials-scraper
streamlit run updated_frontend.py
```

Or use the alternative version:
```bash
streamlit run updated_frontend2.py
```

**Access:** Open your browser to `http://localhost:8501` (Streamlit default port)

## Dependencies

Key packages included in `requirements.txt`:

| Package | Purpose |
|---------|---------|
| `playwright` | Browser automation for Google Maps |
| `requests` | HTTP requests for website scraping |
| `beautifulsoup4` | HTML parsing |
| `pandas` | Data manipulation and CSV/Excel export |
| `openpyxl` | Excel file creation |
| `streamlit` | Web UI framework (for social media scraper) |
| `python-dotenv` | Environment variable management |
| `httpx` | Async HTTP client (for API calls) |

## Configuration & Customization

### Google Maps Scraper
- **Edit XPath selectors** in `scraper.py` (lines 115-119) to adapt for Google Maps UI changes
- **Modify Business class** to capture additional fields
- **Adjust headless parameter** to `headless=True` for background operation

### Website Scraper
- **Edit subpages list** (line 85 in MARK.py) to search different pages
- **Modify regex patterns** (lines 19-20) for different data extraction
- **Adjust worker count** (line 128) for parallel processing speed

### Social Media Scraper
- **Add/remove fields** in the FIELDS list (updated_frontend2.py line 20)
- **Configure search regions** using the `gl` parameter in `fetch_google_search()`

## Important Notes

### Rate Limiting
- Website scraper uses 10 concurrent workers by default - adjust based on target server capacity
- Add delays between requests to avoid blocking

### Legal Considerations
- Always check website `robots.txt` and terms of service before scraping
- Respect `robots.txt` rules
- Use appropriate User-Agent headers
- Consider the legal implications in your jurisdiction

### Error Handling
- Website scraper silently handles errors to prevent crashes
- Check output CSV for empty fields if scraping fails for specific sites
- Monitor console output for detailed error messages

## Troubleshooting

### Playwright Issues
```bash
# Reinstall Playwright
playwright install --with-deps
```

### API Key Issues (Social Media Scraper)
- Verify `.env` file exists in `socials-scraper/` directory
- Check API key validity at respective API provider websites
- Ensure API keys have necessary scopes enabled

### No Results from Google Maps
- Browser may have closed - check console errors
- Wait for page loads with longer timeouts if internet is slow
- Check if XPath selectors need updating due to UI changes

### CSV Not Generated
- Verify `websites.txt` file exists and has valid URLs
- Check file permissions in the project directory
- Ensure all URLs are properly formatted with `http://` or `https://`

## Output Files

### Google Maps Scraper
- **Format**: Excel (.xlsx) and CSV (.csv)
- **Columns**: name, address, website, phone_number, reviews_count, reviews_average
- **Location**: `output/` directory

### Website Scraper
- **Format**: CSV
- **Columns**: business_name, doctor, email
- **Location**: Root directory as `scraped_data.csv`

### Social Media Scraper
- **Exportable**: Yes, CSV export available in Streamlit UI

## Performance Tips

1. **Google Maps Scraper**
   - Reduce `total` parameter for faster execution
   - Run multiple searches sequentially instead of parallel
   - Close other browser windows to reduce resource usage

2. **Website Scraper**
   - Reduce `max_workers` if getting IP blocked
   - Add `time.sleep()` between requests for better politeness
   - Use proxy rotation for large-scale scraping

3. **Social Media Scraper**
   - Cache API results to avoid duplicate calls
   - Use pagination to manage large result sets

## Next Steps & Improvements

Potential enhancements:
- [ ] Add proxy rotation support
- [ ] Implement data deduplication
- [ ] Add email verification
- [ ] Create dashboard for results visualization
- [ ] Add database storage option
- [ ] Implement retry logic with exponential backoff
- [ ] Add logging functionality
- [ ] Support for more social media platforms

## License

This project is provided as-is for educational and authorized commercial use. Ensure compliance with local laws and website terms of service.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in console output
3. Verify all input files are properly formatted
4. Check internet connectivity for API-based scrapers

---

**Last Updated**: December 30, 2025
