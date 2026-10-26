"""scraper/product_scraper.py

Source-specific parsing functions for PriceWise.

Each function takes HTML text and returns a list of product dictionaries.
If a source cannot be parsed or returns anti-bot responses, return an empty list.

IMPORTANT:
- These parsers are examples for PERMITTED sources only.
- Do NOT use these on websites that prohibit scraping.
- Always verify permission (robots.txt, terms of service) before scraping.
"""

from __future__ import annotations
import logging
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger("pricewise_scraper")


def _clean_price(text: str) -> float | None:
    """Extract numeric price from text like '₹1,299' or '$19.99'."""
    if not text:
        return None
    # Remove currency symbols, commas, extra whitespace
    cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _clean_discount(text: str) -> float | None:
    """Extract discount percentage from text like '20%' or '20% off'."""
    if not text:
        return None
    # Extract number before % sign
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _clean_rating(text: str) -> float | None:
    """Extract rating from text like '4.5' or '4.5 out of 5'."""
    if not text:
        return None
    # Extract first number (could be integer or decimal)
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        try:
            val = float(match.group(1))
            # Assume rating is out of 5 if > 5, normalize
            if val > 5:
                val = val / 20 * 5  # If out of 100, convert to 5 scale
            elif val > 10:
                val = val / 2  # If out of 10, convert to 5 scale
            return min(5.0, max(0.0, val))  # Clamp to 0-5
        except ValueError:
            return None
    return None


def parse_example_site(html_text: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Example parser for a permitted site.
    Replace this with actual parsing logic for your permitted source.
    This is a placeholder that returns sample data for demonstration.
    """
    logger.info("[INFO] Parsing example site (placeholder)")

    # In a real implementation, you would parse the HTML here
    # For now, we return empty list to demonstrate the structure
    # When you have a permitted source, implement actual parsing

    # Example of what a real parser might return:
    # products = [
    #     {
    #         "product_name": "Example Product",
    #         "category": "Electronics",
    #         "platform": "Example Store",
    #         "price": 1299.0,
    #         "original_price": 1999.0,
    #         "discount": 35.0,
    #         "rating": 4.5,
    #         "availability": "In Stock",
    #         "product_url": "https://example.com/product/1",
    #         "scraped_date": pd.Timestamp.now().strftime("%Y-%m-%d")
    #     }
    # ]
    # return products

    return []


def parse_permitted_api(json_data: dict) -> List[Dict[str, Any]]:
    """
    Example parser for a permitted API endpoint.
    Replace with actual API response parsing.
    """
    logger.info("[INFO] Parsing permitted API (placeholder)")
    # Implement according to the API's response structure
    return []


# Add more parsers as you verify permission for specific sources
# Each parser should be named consistently with what's in scraper_config.SOURCES