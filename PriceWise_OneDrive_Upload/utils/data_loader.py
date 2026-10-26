"""utils/data_loader.py

All CSV loading, column detection, and basic data cleaning for PriceWise.

Design goals:
- Never crash if optional columns are missing.
- Keep column mapping in one place (COLUMN_MAP).
- If the real CSV is missing, create a small SAMPLE CSV at the expected path.
"""

from __future__ import annotations

import os
import re

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------
# Column name mapping — edit these if your Colab CSV uses different names
# -----------------------------------------------------------------------
COLUMN_MAP: dict[str, list[str]] = {
    "product_name": ["product_name", "name", "title", "product"],
    "category": ["category", "cat", "type"],
    "platform": ["platform", "store", "retailer", "source", "website"],
    "price": ["price", "current_price", "selling_price", "sale_price"],
    "original_price": ["original_price", "mrp", "market_price", "list_price"],
    "discount": ["discount", "discount_percent", "discount_%", "off"],
    "rating": ["rating", "stars", "score", "avg_rating"],
    "availability": ["availability", "in_stock", "stock", "available"],
    "product_url": ["product_url", "url", "link", "product_link"],
    "scraped_date": ["scraped_date", "date", "timestamp", "scraped_at"],
}

SAMPLE_MARKER_COL = "pricewise_sample"

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "pricewise_data.csv",
)


def _resolve_columns(df: pd.DataFrame) -> dict[str, str]:
    """Map canonical column names (product_name, price, ...) to actual df columns."""
    actual_cols = {c.lower().strip(): c for c in df.columns}
    resolved: dict[str, str] = {}

    for canonical, aliases in COLUMN_MAP.items():
        for alias in aliases:
            key = alias.lower().strip()
            if key in actual_cols:
                resolved[canonical] = actual_cols[key]
                break

    return resolved


def _clean_numeric_series(s: pd.Series) -> pd.Series:
    """Remove currency symbols/commas and coerce to numeric."""
    # Ensure strings for regex replacement.
    ss = s.astype(str).str.strip()
    ss = ss.replace({"nan": None, "None": None})

    # Remove ₹, $, commas, whitespace.
    ss = ss.str.replace(r"[₹$,\s,]", "", regex=True)

    # Empty => NaN
    ss = ss.replace({"": None})

    return pd.to_numeric(ss, errors="coerce")


def _create_sample_data() -> pd.DataFrame:
    """Return a small sample dataframe for development/demo use."""
    data = {
        "product_name": [
            "iPhone 16 128GB",
            "iPhone 16 128GB",
            "iPhone 16 128GB",
            "Samsung Galaxy S24",
            "Samsung Galaxy S24",
            "OnePlus 12R 8GB",
            "OnePlus 12R 8GB",
            "Sony WH-1000XM5 Headphones",
            "Sony WH-1000XM5 Headphones",
            "Apple MacBook Air M2",
            "Apple MacBook Air M2",
            "Boat Airdopes 141",
            "Boat Airdopes 141",
        ],
        "category": [
            "Smartphones",
            "Smartphones",
            "Smartphones",
            "Smartphones",
            "Smartphones",
            "Smartphones",
            "Smartphones",
            "Audio",
            "Audio",
            "Laptops",
            "Laptops",
            "Audio",
            "Audio",
        ],
        "platform": [
            "Amazon",
            "Flipkart",
            "Croma",
            "Amazon",
            "Flipkart",
            "Amazon",
            "Flipkart",
            "Amazon",
            "Croma",
            "Amazon",
            "Flipkart",
            "Amazon",
            "Flipkart",
        ],
        "price": [69999, 68499, 70999, 74999, 73499, 29999, 29499, 26990, 27990, 109990, 108999, 1299, 1199],
        "original_price": [79900, 79900, 79900, 84999, 84999, 34999, 34999, 34990, 34990, 124900, 124900, 1799, 1799],
        "rating": [4.5, 4.6, 4.3, 4.4, 4.5, 4.3, 4.4, 4.7, 4.6, 4.8, 4.7, 4.1, 4.2],
        "availability": [
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
            "In Stock",
        ],
        # Discount is optional; sample includes it so UI can show it immediately.
        "discount": [12, 14, 11, 12, 14, 14, 16, 23, 20, 12, 13, 28, 33],
        "product_url": [""] * 13,
        "scraped_date": ["2024-12-01"] * 13,
        SAMPLE_MARKER_COL: [1] * 13,
    }
    return pd.DataFrame(data)


def _ensure_data_csv_exists() -> None:
    """Create sample CSV at the expected path if it doesn't exist."""
    if os.path.exists(DATA_PATH):
        return

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df = _create_sample_data()
    df.to_csv(DATA_PATH, index=False)


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, dict[str, str], bool]:
    """Load product data from CSV.

    Returns:
      (df, col_map, is_sample)
    """
    _ensure_data_csv_exists()

    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(), {}, True

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        st.error(f"Could not read CSV file: {e}")
        return pd.DataFrame(), {}, True

    if df.empty:
        return df, {}, False

    col_map = _resolve_columns(df)

    is_sample = False
    if SAMPLE_MARKER_COL in df.columns:
        try:
            marker_val = df[SAMPLE_MARKER_COL].dropna().iloc[0]
            is_sample = bool(marker_val) and str(marker_val) != "0"
        except Exception:
            is_sample = True

    # Clean numeric columns when we have them.
    for canonical in ["price", "original_price", "discount", "rating"]:
        if canonical in col_map:
            df[col_map[canonical]] = _clean_numeric_series(df[col_map[canonical]])

    # Compute discount if missing but we can derive it.
    if "discount" not in col_map and "price" in col_map and "original_price" in col_map:
        pcol = col_map["price"]
        opcol = col_map["original_price"]
        with pd.option_context("mode.use_inf_as_na", True):
            df["discount"] = ((df[opcol] - df[pcol]) / df[opcol] * 100).round(1)
        col_map["discount"] = "discount"

    return df, col_map, is_sample


def get_column(df: pd.DataFrame, col_map: dict[str, str], canonical: str):
    """Safely get a df series by canonical column name; returns None if unavailable."""
    if canonical not in col_map:
        return None
    col = col_map[canonical]
    if col not in df.columns:
        return None
    return df[col]


@st.cache_data(show_spinner=False)
def get_categories(df: pd.DataFrame, col_map: dict[str, str]) -> list[str]:
    if "category" not in col_map:
        return []
    col = col_map["category"]
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).unique().tolist())


@st.cache_data(show_spinner=False)
def get_platforms(df: pd.DataFrame, col_map: dict[str, str]) -> list[str]:
    if "platform" not in col_map:
        return []
    col = col_map["platform"]
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).unique().tolist())


def filter_data(
    df: pd.DataFrame,
    col_map: dict[str, str],
    categories=None,
    platforms=None,
    price_min=None,
    price_max=None,
) -> pd.DataFrame:
    """Apply sidebar filters and return a filtered dataframe."""
    if df.empty:
        return df

    filtered = df

    if categories and "category" in col_map:
        cat_col = col_map["category"]
        if cat_col in filtered.columns:
            filtered = filtered[filtered[cat_col].isin(categories)]

    if platforms and "platform" in col_map:
        plat_col = col_map["platform"]
        if plat_col in filtered.columns:
            filtered = filtered[filtered[plat_col].isin(platforms)]

    if "price" in col_map:
        pcol = col_map["price"]
        if pcol in filtered.columns:
            if price_min is not None:
                filtered = filtered[filtered[pcol] >= price_min]
            if price_max is not None:
                filtered = filtered[filtered[pcol] <= price_max]

    return filtered
