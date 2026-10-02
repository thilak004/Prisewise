"""
Configuration for the PriceWise scraper.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Scraper mode: "demo" or "live"
# Demo mode uses local sample data and does not make live requests.
# Live mode attempts to scrape from permitted sources.
SCRAPER_MODE = "demo"  # Change to "live" when you have permitted sources and want to scrape live

# Request settings
REQUEST_DELAY_SECONDS = 5  # Delay between requests to the same domain
REQUEST_TIMEOUT = 15       # Timeout for each request in seconds
MAX_RETRIES = 2            # Maximum number of retries for temporary failures

# User-Agent string
USER_AGENT = "PriceWise/1.0 Educational price analysis project"

# Caching
CACHE_ENABLED = True
CACHE_DIR = BASE_DIR / "scraper" / "cache"

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Data directories
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Ensure data directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Output files
RAW_DATA_FILE = RAW_DATA_DIR / "pricewise_raw.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "pricewise_data.csv"
# Also output to the location expected by the existing Streamlit application
STREAMLIT_DATA_FILE = BASE_DIR / "data" / "pricewise_data.csv"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Sources to scrape
# Each source is a dictionary with:
#   - name: identifier for the source
#   - base_url: base URL for the source
#   - permitted: boolean indicating if we have verified that scraping is allowed
#   - delay: optional override for request delay (seconds)
#   - paths: list of paths to scrape (relative to base_url)
#   - parse_function: name of the function in product_scraper.py to use for parsing
SOURCES = [
    {
        "name": "example_permitted_site",
        "base_url": "https://example.com",
        "permitted": False,  # Set to True only after verifying permission (robots.txt, terms of service)
        "delay": REQUEST_DELAY_SECONDS,
        "paths": ["/products", "/deals"],
        "parse_function": "parse_example_site",
    },
    # Add more sources here as you verify permission
]

# Demo mode sample data location
DEMO_SAMPLE_DATA_FILE = BASE_DIR / "data" / "sample_data.csv"

# Environment variables for API keys, etc. (load from .env file)
# Example:
#   API_KEY_EXAMPLE = os.getenv("API_KEY_EXAMPLE")
# Remember to add .env to .gitignore and create .env.example