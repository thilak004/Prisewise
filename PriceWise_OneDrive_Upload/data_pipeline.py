"""PriceWise Data Pipeline

Orchestrates the data collection + cleaning process for the PriceWise application.

Goals (as required):
- Safe by default: DEMO mode should never hit live websites.
- LIVE mode must be intentional and follow conservative rate limits.
- Write:
    data/raw/pricewise_raw.csv
    data/processed/pricewise_data.csv
    data/pricewise_data.csv (for the existing Streamlit app)
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from scraper.base_scraper import BaseScraper
from scraper.product_scraper import parse_example_site, parse_permitted_api
from scraper.scraper_config import (
    SCRAPER_MODE,
    RAW_DATA_FILE,
    PROCESSED_DATA_FILE,
    STREAMLIT_DATA_FILE,
    SOURCES,
    DEMO_SAMPLE_DATA_FILE,
    USER_AGENT,
    REQUEST_DELAY_SECONDS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
)


# ------------------------- Logging -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("pricewise_pipeline")


# ------------------------- Demo data -------------------------

def create_demo_sample_data() -> pd.DataFrame:
    """Create a small demo dataset (20–100 offers).

    This is ONLY used in DEMO mode as a safe development/demo dataset.
    """
    scraped_date = datetime.now().strftime("%Y-%m-%d")

    products = [
        ("iPhone 16 128GB", "Smartphones"),
        ("iPhone 16 256GB", "Smartphones"),
        ("Samsung Galaxy S24", "Smartphones"),
        ("Samsung Galaxy S24+", "Smartphones"),
        ("OnePlus 12R 8GB", "Smartphones"),
        ("Redmi Note 14 Pro", "Smartphones"),
        ("Realme 12 Pro", "Smartphones"),
        ("Google Pixel 9", "Smartphones"),
        ("Motorola Edge 50", "Smartphones"),
        ("Sony WH-1000XM5", "Audio"),
        ("Bose QuietComfort", "Audio"),
        ("Apple Watch Series 9", "Wearables"),
        ("Apple AirPods Pro 2", "Audio"),
        ("Dell XPS 13", "Laptops"),
        ("HP Pavilion 15", "Laptops"),
        ("MacBook Air M2", "Laptops"),
        ("Asus Vivobook 14", "Laptops"),
        ("Samsung Galaxy Tab S10", "Tablets"),
        ("Lenovo Tab P12", "Tablets"),
        ("Amazon Kindle Paperwhite", "E-readers"),
    ]

    platforms = ["Amazon", "Flipkart", "Croma"]

    rows: List[Dict[str, Any]] = []

    # Deterministic, small sample generation.
    # (We are not scraping; this is demo-only data.)
    for idx, (pname, category) in enumerate(products):
        base_original = 1000 + (idx * 137)  # just a demo baseline
        base_price = base_original * 0.85

        for j, platform in enumerate(platforms):
            # add small platform variation
            price = base_price * (1 - (j * 0.03))
            original_price = base_original * (1 - (j * 0.01))

            # Discount % derived from demo fields
            discount = None
            if original_price and original_price > 0:
                discount = round(((original_price - price) / original_price) * 100, 1)

            # Rating demo (0-5)
            rating = round(3.8 + ((idx + j) % 10) * 0.08, 1)
            rating = max(0.0, min(5.0, rating))

            rows.append(
                {
                    "product_name": pname,
                    "category": category,
                    "platform": platform,
                    "price": round(price, 0),
                    "original_price": round(original_price, 0),
                    "discount": discount,
                    "rating": rating,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": scraped_date,
                    # Marker column so Streamlit can clearly label sample/demo data.
                    "pricewise_sample": 1,
                }
            )

    # This creates 20 products * 3 platforms = 60 offers.
    df = pd.DataFrame(rows)

    # Normalize numeric columns.
    for c in ["price", "original_price", "discount", "rating"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def load_sample_data() -> pd.DataFrame:
    """Load or create local sample data.

    The existing Streamlit app shows a "sample data" notice when the
    `pricewise_sample` column is present.
    """
    try:
        if DEMO_SAMPLE_DATA_FILE.exists():
            df = pd.read_csv(DEMO_SAMPLE_DATA_FILE)
            return df

        df = create_demo_sample_data()
        DEMO_SAMPLE_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DEMO_SAMPLE_DATA_FILE, index=False)
        return df
    except Exception as e:
        logger.error(f"[ERROR] Failed to load/create demo sample data: {e}")
        # As a last resort return an empty frame.
        return pd.DataFrame()


# ------------------------- Scraping orchestration -------------------------

def scrape_source(scraper: BaseScraper, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape a single source according to its configuration."""
    name = source_config["name"]
    base_url = source_config["base_url"]
    paths = source_config.get("paths", [])
    parse_func_name = source_config.get("parse_function")

    logger.info(f"[INFO] Processing source: {name} ({base_url})")

    parse_func = globals().get(parse_func_name)
    if not parse_func:
        logger.error(f"[ERROR] Parse function '{parse_func_name}' not found for source '{name}'")
        return []

    all_products: List[Dict[str, Any]] = []

    for path in paths:
        logger.info(f"[INFO] Scraping path: {path}")
        result = scraper.fetch(path)

        if result.error:
            # Stop source on 403/429/robots disallow/demo mode.
            if result.error in {"Access forbidden", "Rate limited", "Robots disallow", "Demo mode"}:
                logger.warning(f"[SKIP] {result.error} for {name} - stopping this source")
                break

            logger.warning(f"[WARNING] Error fetching {path}: {result.error}")
            continue

        if not result.text:
            logger.warning(f"[WARNING] Empty response for {path}")
            continue

        try:
            products = parse_func(result.text, base_url)
            if products:
                logger.info(f"[INFO] Parsed {len(products)} products from {path}")
                all_products.extend(products)
            else:
                logger.info(f"[INFO] No products parsed from {path}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to parse {path}: {e}")

    return all_products


# ------------------------- Cleaning -------------------------

def ensure_schema_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure expected columns exist; fill missing with NA."""
    required = [
        "product_name",
        "category",
        "platform",
        "price",
        "original_price",
        "discount",
        "rating",
        "availability",
        "product_url",
        "scraped_date",
    ]

    out = df.copy()
    for col in required:
        if col not in out.columns:
            out[col] = pd.NA

    return out


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean + validate collected data.

    IMPORTANT: No "inventing" missing values. If a field is missing in
    the raw dataset, it stays missing (NA).
    """
    if df is None or df.empty:
        return pd.DataFrame()

    logger.info("[INFO] Starting data cleaning process")
    initial_count = len(df)

    cleaned = ensure_schema_columns(df)

    # Strip + normalize strings.
    for col in ["product_name", "category", "platform", "availability"]:
        cleaned[col] = cleaned[col].astype(str).str.strip()
        cleaned[col] = cleaned[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    # Convert numeric fields.
    for col in ["price", "original_price", "discount", "rating"]:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    # Validate ranges (keep NA if invalid/missing).
    if "price" in cleaned.columns:
        cleaned.loc[~cleaned["price"].between(1, 1_000_000_000_000, inclusive="both"), "price"] = pd.NA

    if "discount" in cleaned.columns:
        cleaned.loc[~cleaned["discount"].between(0, 100, inclusive="both"), "discount"] = pd.NA

    if "rating" in cleaned.columns:
        cleaned.loc[~cleaned["rating"].between(0, 5, inclusive="both"), "rating"] = pd.NA

    # Normalize dates.
    if "scraped_date" in cleaned.columns:
        cleaned["scraped_date"] = pd.to_datetime(cleaned["scraped_date"], errors="coerce")
        cleaned["scraped_date"] = cleaned["scraped_date"].dt.strftime("%Y-%m-%d")

    # Remove exact duplicates.
    cleaned = cleaned.drop_duplicates()

    # Essential fields: product_name + price.
    before_essential = len(cleaned)
    cleaned = cleaned.dropna(subset=["product_name", "price"])
    logger.info(f"[INFO] Removed {before_essential - len(cleaned)} rows missing essential fields")

    # Remove duplicates by product_name + platform, keeping lowest price.
    if "product_name" in cleaned.columns:
        if "platform" in cleaned.columns and cleaned["platform"].notna().any():
            subset = ["product_name", "platform"]
        else:
            subset = ["product_name"]

        cleaned = cleaned.sort_values("price", na_position="last")
        before_dupes = len(cleaned)
        cleaned = cleaned.drop_duplicates(subset=subset, keep="first")
        logger.info(
            f"[INFO] Removed {before_dupes - len(cleaned)} duplicate products (same name+platform)"
        )

    logger.info(f"[INFO] Data cleaning complete: {initial_count} -> {len(cleaned)} products")
    return cleaned.reset_index(drop=True)


# ------------------------- Saving -------------------------

def save_data(df_raw: pd.DataFrame, df_processed: pd.DataFrame) -> None:
    RAW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    df_raw.to_csv(RAW_DATA_FILE, index=False)
    logger.info(f"[INFO] Saved raw data to {RAW_DATA_FILE} ({len(df_raw)} rows)")

    df_processed.to_csv(PROCESSED_DATA_FILE, index=False)
    logger.info(
        f"[INFO] Saved processed data to {PROCESSED_DATA_FILE} ({len(df_processed)} rows)"
    )

    df_processed.to_csv(STREAMLIT_DATA_FILE, index=False)
    logger.info(f"[INFO] Saved processed data to Streamlit location {STREAMLIT_DATA_FILE}")


def print_pipeline_report(mode: str, raw_count: int, processed_count: int) -> None:
    print("\n" + "=" * 50)
    print("PriceWise Data Pipeline Report")
    print("=" * 50)
    print(f"Mode: {mode.upper()}")
    print(f"Products collected (raw): {raw_count}")
    print(f"Products after cleaning: {processed_count}")
    print(f"Raw data saved to: {RAW_DATA_FILE}")
    print(f"Processed data saved to: {PROCESSED_DATA_FILE}")
    print(f"Streamlit data saved to: {STREAMLIT_DATA_FILE}")
    print("=" * 50)


# ------------------------- Main -------------------------

def main() -> None:
    logger.info("[INFO] Starting PriceWise data pipeline")
    logger.info(f"[INFO] Running in {SCRAPER_MODE} mode")

    if SCRAPER_MODE == "demo":
        df_raw = load_sample_data()
        df_processed = clean_data(df_raw)
        save_data(df_raw, df_processed)
        print_pipeline_report(SCRAPER_MODE, len(df_raw), len(df_processed))
        logger.info("[INFO] PriceWise data pipeline completed successfully")
        return

    # LIVE mode
    all_raw_products: List[Dict[str, Any]] = []

    sources_processed = 0
    sources_skipped = 0

    for source_config in SOURCES:
        name = source_config.get("name", "unknown")
        if not source_config.get("permitted", False):
            logger.warning(f"[SKIP] Source '{name}' not marked as permitted in config. Skipping.")
            sources_skipped += 1
            continue

        base_url = source_config.get("base_url", "")
        scraper = BaseScraper(
            base_url=base_url,
            request_delay_seconds=REQUEST_DELAY_SECONDS,
            request_timeout=REQUEST_TIMEOUT,
            max_retries=MAX_RETRIES,
            user_agent=USER_AGENT,
            mode=SCRAPER_MODE,
        )

        try:
            products = scrape_source(scraper, source_config)
            if products:
                all_raw_products.extend(products)
                sources_processed += 1
            else:
                sources_skipped += 1
        except Exception as e:
            logger.error(f"[ERROR] Source '{name}' failed unexpectedly: {e}")
            sources_skipped += 1

    df_raw = pd.DataFrame(all_raw_products)
    logger.info(f"[INFO] Collected {len(df_raw)} raw products")
    logger.info(f"[INFO] Processed: {sources_processed}, Skipped: {sources_skipped}")

    if df_raw.empty:
        logger.warning("[WARNING] All sources produced no data. Falling back to demo sample data.")
        df_raw = load_sample_data()

    df_processed = clean_data(df_raw)
    save_data(df_raw, df_processed)
    print_pipeline_report(SCRAPER_MODE, len(df_raw), len(df_processed))
    logger.info("[INFO] PriceWise data pipeline completed successfully")


if __name__ == "__main__":
    main()
