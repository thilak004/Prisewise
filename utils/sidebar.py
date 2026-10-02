"""utils/sidebar.py

Sidebar components shared across pages.
"""

from __future__ import annotations

import os
import streamlit as st

from utils.data_loader import get_categories, get_platforms, filter_data
from utils.formatting import format_inr


def render_brand_sidebar(logo_path: str | None, name: str = "PriceWise"):
    """Brand + navigation header in sidebar."""
    if logo_path and os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=48)
    st.sidebar.markdown(f"### {name}")


def sidebar_filters(df, col_map, show_navigation: bool = True):
    """Render sidebar filters and return filtered dataframe.

    If a column is missing, its filter UI is hidden.
    """
    if show_navigation:
        st.sidebar.divider()
        st.sidebar.page_link("pages/home.py", label="Home", icon="🏠")
        st.sidebar.page_link("pages/comparison.py", label="Compare", icon="📊")
        st.sidebar.page_link("pages/analytics.py", label="Analytics", icon="📈")
        st.sidebar.page_link("pages/about.py", label="About", icon="ℹ️")

    st.sidebar.divider()
    st.sidebar.subheader("Filters")

    categories = None
    if "category" in col_map and col_map["category"] in df.columns:
        cats = get_categories(df, col_map)
        categories = st.sidebar.multiselect("Category", options=cats, default=[])
        if categories:
            categories = list(categories)
        else:
            categories = None

    platforms = None
    if "platform" in col_map and col_map["platform"] in df.columns:
        plats = get_platforms(df, col_map)
        platforms = st.sidebar.multiselect("Platform", options=plats, default=[])
        if platforms:
            platforms = list(platforms)
        else:
            platforms = None

    price_min = None
    price_max = None
    if "price" in col_map and col_map["price"] in df.columns:
        pcol = col_map["price"]
        p = df[pcol]
        p = p.dropna()
        if not p.empty:
            lo = int(p.min())
            hi = int(p.max())
            if lo < hi:
                price_min, price_max = st.sidebar.slider(
                    "Price range",
                    min_value=lo,
                    max_value=hi,
                    value=(lo, hi),
                    format="%d",
                )
            else:
                st.sidebar.text(f"Price: {format_inr(lo)}")
                price_min, price_max = lo, hi

    filtered = filter_data(
        df,
        col_map,
        categories=categories,
        platforms=platforms,
        price_min=price_min,
        price_max=price_max,
    )

    return filtered
