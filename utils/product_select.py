"""utils/product_select.py

Product selection helpers for PriceWise.

Goal:
- On the Home page, show one row per product.
- For each product, select the *lowest available price* across platforms.
- Never invent product data. Everything comes from the CSV.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def products_overview(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """Return one row per product_name.

    The selected row for each product is chosen by lowest available price.
    If price is missing/unavailable, we fall back to the first row for that product.

    Output columns (only included when input columns exist):
    - product_name
    - category
    - platform
    - price (current/lowest)
    - original_price
    - discount
    - rating
    - availability
    - product_url
    """
    if df.empty or "product_name" not in col_map or col_map["product_name"] not in df.columns:
        return pd.DataFrame()

    prod_col = col_map["product_name"]
    price_col = col_map.get("price")

    # Work on a copy so we can safely coerce.
    base = df.copy()

    if price_col and price_col in base.columns:
        base[price_col] = pd.to_numeric(base[price_col], errors="coerce")

    # Pick representative row per product (lowest available price, fallback to first row).
    if price_col and price_col in base.columns:
        sorted_base = base.sort_values(by=[prod_col, price_col], ascending=[True, True], na_position="last")
        overview = sorted_base.drop_duplicates(subset=[prod_col], keep="first").copy()
    else:
        overview = base.sort_index().drop_duplicates(subset=[prod_col], keep="first").copy()

    # Build output with canonical names.
    out = pd.DataFrame({"product_name": overview[prod_col]})

    for canonical, output_name in [
        ("category", "category"),
        ("platform", "platform"),
        ("original_price", "original_price"),
        ("discount", "discount"),
        ("rating", "rating"),
        ("availability", "availability"),
        ("product_url", "product_url"),
    ]:
        if canonical in col_map and col_map[canonical] in overview.columns:
            out[output_name] = overview[col_map[canonical]]

    if "price" in col_map and col_map["price"] in overview.columns:
        out["price"] = overview[col_map["price"]]

    # Sort by lowest price if present.
    if "price" in out.columns:
        out = out.sort_values("price", ascending=True, na_position="last")
    else:
        out = out.sort_values("product_name")

    return out.reset_index(drop=True)


def search_overview(overview_df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Filter overview rows by product_name contains query (case-insensitive)."""
    if overview_df.empty:
        return overview_df
    q = (query or "").strip()
    if not q:
        return overview_df
    return overview_df[overview_df["product_name"].astype(str).str.contains(q, case=False, na=False)].copy()


def fuzzy_search_products(df: pd.DataFrame, col_map: dict, query: str, max_results: int = 10) -> list:
    """Fuzzy search for product names — returns list of matching product names.

    Uses simple substring + word-boundary matching for auto-complete.
    """
    if df.empty or "product_name" not in col_map:
        return []

    prod_col = col_map["product_name"]
    if prod_col not in df.columns:
        return []

    q = (query or "").strip().lower()
    if not q:
        return []

    all_products = df[prod_col].dropna().astype(str).unique().tolist()

    # Score each product by match quality
    scored = []
    for prod in all_products:
        prod_lower = prod.lower()
        if q == prod_lower:
            scored.append((prod, 100))  # exact match
        elif prod_lower.startswith(q):
            scored.append((prod, 80))  # starts with query
        elif q in prod_lower:
            scored.append((prod, 60))  # contains query
        else:
            # Check if all words in query appear in product
            query_words = q.split()
            if all(word in prod_lower for word in query_words):
                scored.append((prod, 40))  # all words present

    scored.sort(key=lambda x: -x[1])
    return [name for name, _ in scored[:max_results]]
