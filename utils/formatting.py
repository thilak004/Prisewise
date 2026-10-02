"""utils/formatting.py

Small formatting helpers for PriceWise.
"""

from __future__ import annotations

import pandas as pd
import math


def _is_number(x) -> bool:
    try:
        return x is not None and not (isinstance(x, float) and math.isnan(x))
    except Exception:
        return False


def format_inr(value) -> str:
    """Format a numeric value as Indian Rupees."""
    if value is None:
        return "N/A"
    try:
        if isinstance(value, str):
            if not value.strip():
                return "N/A"
            value = float(value)
        if not _is_number(value):
            return "N/A"
        # Most prices are integers in INR; format without decimals.
        return f"₹{value:,.0f}"
    except Exception:
        return "N/A"


def format_percent(value) -> str:
    if value is None:
        return "N/A"
    try:
        if isinstance(value, str):
            value = float(value)
        if not _is_number(value):
            return "N/A"
        return f"{value:.1f}%"
    except Exception:
        return "N/A"


def safe_str(value) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value)


def is_valid_http_url(url: str | None) -> bool:
    if not url:
        return False
    u = str(url).strip()
    if not u:
        return False
    return u.startswith("http://") or u.startswith("https://")
