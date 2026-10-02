"""utils/analysis.py

Small, beginner-friendly analysis helpers for PriceWise.
All functions are defensive: they work even when some optional columns are missing.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import streamlit as st


# ── Feature #2: Best Deal Recommendation Engine ──────────────────────────────

@st.cache_data(show_spinner=False)
def best_deal_score(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """Compute a composite 'Best Deal' score for each product-platform offer.

    Score components (all normalized 0-1, higher = better deal):
    - Price (lower is better): 40% weight
    - Discount (higher is better): 25% weight
    - Rating (higher is better): 20% weight
    - Availability (In Stock = 1, else 0.5): 15% weight

    Returns DataFrame with columns: product_name, platform, price, score, deal_tier
    """
    if df.empty or "price" not in col_map:
        return pd.DataFrame()

    prod_col = col_map.get("product_name")
    price_col = col_map["price"]
    plat_col = col_map.get("platform")
    disc_col = col_map.get("discount")
    rat_col = col_map.get("rating")
    avail_col = col_map.get("availability")

    if not prod_col or prod_col not in df.columns:
        return pd.DataFrame()

    work = df.copy()
    work["price_num"] = pd.to_numeric(work[price_col], errors="coerce")

    # Normalize price (lower = better, so invert)
    price_min = work["price_num"].min()
    price_max = work["price_num"].max()
    if price_max > price_min:
        work["price_score"] = 1 - (work["price_num"] - price_min) / (price_max - price_min)
    else:
        work["price_score"] = 0.5

    # Discount score
    if disc_col and disc_col in work.columns:
        work["discount_num"] = pd.to_numeric(work[disc_col], errors="coerce").fillna(0)
        disc_max = work["discount_num"].max()
        work["discount_score"] = work["discount_num"] / disc_max if disc_max > 0 else 0
    else:
        work["discount_score"] = 0

    # Rating score
    if rat_col and rat_col in work.columns:
        work["rating_num"] = pd.to_numeric(work[rat_col], errors="coerce").fillna(0)
        work["rating_score"] = work["rating_num"] / 5.0
    else:
        work["rating_score"] = 0

    # Availability score
    if avail_col and avail_col in work.columns:
        work["avail_score"] = work[avail_col].apply(
            lambda x: 1.0 if str(x).strip().lower() in ("in stock", "available", "yes", "true", "1") else 0.5
        )
    else:
        work["avail_score"] = 0.5

    # Composite score
    work["score"] = (
        work["price_score"] * 0.40
        + work["discount_score"] * 0.25
        + work["rating_score"] * 0.20
        + work["avail_score"] * 0.15
    )

    # Deal tier
    def _tier(s):
        if s >= 0.75:
            return "Excellent"
        elif s >= 0.55:
            return "Good"
        elif s >= 0.35:
            return "Average"
        else:
            return "Poor"

    work["deal_tier"] = work["score"].apply(_tier)

    # Build output
    out_cols = {"product_name": prod_col, "price": "price_num"}
    if plat_col and plat_col in work.columns:
        out_cols["platform"] = plat_col
    if disc_col and disc_col in work.columns:
        out_cols["discount"] = disc_col
    if rat_col and rat_col in work.columns:
        out_cols["rating"] = rat_col

    out = work[list(out_cols.keys())].rename(columns={v: k for k, v in out_cols.items()})
    out["score"] = work["score"].round(3)
    out["deal_tier"] = work["deal_tier"]

    return out.sort_values("score", ascending=False).reset_index(drop=True)


# ── Feature #7: Category-wise Average Discount ───────────────────────────────

@st.cache_data(show_spinner=False)
def category_discount_summary(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """Average discount per category — which category has the deepest discounts?"""
    if df.empty or "category" not in col_map or "discount" not in col_map:
        return pd.DataFrame()

    cat_col = col_map["category"]
    disc_col = col_map["discount"]

    if cat_col not in df.columns or disc_col not in df.columns:
        return pd.DataFrame()

    out = (
        df.dropna(subset=[cat_col])
        .groupby(cat_col)[disc_col]
        .agg(avg_discount="mean", max_discount="max", min_discount="min", count="size")
        .reset_index()
        .rename(columns={cat_col: "category"})
    )
    out["avg_discount"] = out["avg_discount"].round(1)
    return out.sort_values("avg_discount", ascending=False)


# ── Feature #13: ML Price Prediction ─────────────────────────────────────────

@st.cache_data(show_spinner=False)
def train_price_predictor(df: pd.DataFrame, col_map: dict):
    """Train a simple ML model to predict if a price is 'good' (below median).

    Uses scikit-learn Logistic Regression with features:
    - category (one-hot encoded)
    - platform (one-hot encoded)
    - discount
    - rating

    Returns (model, encoder, X_columns, accuracy) or (None, None, None, None) if insufficient data.
    """
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import OneHotEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
    except ImportError:
        return None, None, None, None

    if df.empty or "price" not in col_map:
        return None, None, None, None

    price_col = col_map["price"]
    cat_col = col_map.get("category")
    plat_col = col_map.get("platform")
    disc_col = col_map.get("discount")
    rat_col = col_map.get("rating")

    work = df.copy()
    work["price_num"] = pd.to_numeric(work[price_col], errors="coerce")
    work = work.dropna(subset=["price_num"])

    if len(work) < 20:
        return None, None, None, None

    # Target: price below median = "good deal" (1)
    median_price = work["price_num"].median()
    work["is_good_deal"] = (work["price_num"] < median_price).astype(int)

    # Features
    feature_cols = []
    if cat_col and cat_col in work.columns:
        work["category_str"] = work[cat_col].astype(str)
        feature_cols.append("category_str")
    if plat_col and plat_col in work.columns:
        work["platform_str"] = work[plat_col].astype(str)
        feature_cols.append("platform_str")
    if disc_col and disc_col in work.columns:
        work["discount_num"] = pd.to_numeric(work[disc_col], errors="coerce").fillna(0)
        feature_cols.append("discount_num")
    if rat_col and rat_col in work.columns:
        work["rating_num"] = pd.to_numeric(work[rat_col], errors="coerce").fillna(0)
        feature_cols.append("rating_num")

    if not feature_cols:
        return None, None, None, None

    X = work[feature_cols].copy()
    y = work["is_good_deal"]

    # One-hot encode categorical columns
    cat_features = [c for c in feature_cols if c in ("category_str", "platform_str")]
    num_features = [c for c in feature_cols if c not in ("category_str", "platform_str")]

    encoder = None
    if cat_features:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        X_cat = encoder.fit_transform(X[cat_features])
        cat_col_names = encoder.get_feature_names_out(cat_features)
        X_cat_df = pd.DataFrame(X_cat, columns=cat_col_names, index=X.index)
        X_num = X[num_features] if num_features else pd.DataFrame(index=X.index)
        X_final = pd.concat([X_num, X_cat_df], axis=1)
    else:
        X_final = X

    if len(X_final) < 10:
        return None, None, None, None

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_final, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, encoder, list(X_final.columns), round(accuracy, 3)


def predict_deal_quality(model, encoder, feature_columns, input_data: dict) -> dict:
    """Predict if a given product offer is a 'good deal'.

    input_data should have keys like: category, platform, discount, rating
    Returns dict with prediction (1=good, 0=poor) and probability.
    """
    if model is None:
        return {"prediction": None, "probability": None, "is_good_deal": None}

    try:
        # Build a single-row DataFrame matching training features
        row = {}
        for col in feature_columns:
            row[col] = 0

        # Set numeric features
        if "discount_num" in row:
            row["discount_num"] = float(input_data.get("discount", 0))
        if "rating_num" in row:
            row["rating_num"] = float(input_data.get("rating", 0))

        # Build categorical input for the encoder
        cat_input = {}
        if encoder is not None:
            # Get the categorical feature names the encoder was trained on
            encoder_feature_names = encoder.feature_names_in_
            for enc_name in encoder_feature_names:
                if enc_name == "category_str":
                    cat_input[enc_name] = str(input_data.get("category", ""))
                elif enc_name == "platform_str":
                    cat_input[enc_name] = str(input_data.get("platform", ""))

            if cat_input:
                cat_df = pd.DataFrame([cat_input])
                X_cat = encoder.transform(cat_df)
                cat_col_names = encoder.get_feature_names_out(encoder_feature_names)
                for i, name in enumerate(cat_col_names):
                    if name in row:
                        row[name] = X_cat[0][i]

        X_input = pd.DataFrame([row])[feature_columns]
        pred = model.predict(X_input)[0]
        prob = model.predict_proba(X_input)[0]

        return {
            "prediction": int(pred),
            "probability": round(float(prob[pred]), 3),
            "is_good_deal": bool(pred == 1),
        }
    except Exception as e:
        return {"prediction": None, "probability": None, "is_good_deal": None, "error": str(e)}


# ── Feature #11: Market Share (Platform dominance) ──────────────────────────

@st.cache_data(show_spinner=False)
def platform_market_share(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """Platform market share by number of products and average price."""
    if df.empty or "platform" not in col_map:
        return pd.DataFrame()

    plat_col = col_map["platform"]
    price_col = col_map.get("price")
    prod_col = col_map.get("product_name")

    if plat_col not in df.columns:
        return pd.DataFrame()

    agg_dict = {"product_count": (plat_col, "size")}
    if prod_col and prod_col in df.columns:
        agg_dict["unique_products"] = (prod_col, "nunique")
    if price_col and price_col in df.columns:
        agg_dict["avg_price"] = (price_col, "mean")

    out = (
        df.dropna(subset=[plat_col])
        .groupby(plat_col)
        .agg(**agg_dict)
        .reset_index()
        .rename(columns={plat_col: "platform"})
    )

    if "avg_price" in out.columns:
        out["avg_price"] = out["avg_price"].round(0)

    total = out["product_count"].sum()
    out["market_share_pct"] = (out["product_count"] / total * 100).round(1)

    return out.sort_values("product_count", ascending=False)


# ── Feature #15: Watchlist helpers ──────────────────────────────────────────

def get_watchlist() -> list:
    """Get the current watchlist from session state."""
    return st.session_state.get("watchlist", [])


def add_to_watchlist(product_name: str):
    """Add a product to the watchlist."""
    wl = get_watchlist()
    if product_name not in wl:
        wl.append(product_name)
    st.session_state["watchlist"] = wl


def remove_from_watchlist(product_name: str):
    """Remove a product from the watchlist."""
    wl = get_watchlist()
    if product_name in wl:
        wl.remove(product_name)
    st.session_state["watchlist"] = wl


def is_in_watchlist(product_name: str) -> bool:
    """Check if a product is in the watchlist."""
    return product_name in get_watchlist()


def _num_series(s: pd.Series | None) -> pd.Series | None:
    if s is None:
        return None
    return pd.to_numeric(s, errors="coerce")


@st.cache_data(show_spinner=False)
def basic_stats(df: pd.DataFrame, col_map: dict) -> dict:
    """Return min/max/avg stats for price when available."""
    if df.empty or "price" not in col_map:
        return {}

    price_col = col_map["price"]
    if price_col not in df.columns:
        return {}

    p = _num_series(df[price_col])
    if p is None or p.dropna().empty:
        return {}

    return {
        "min_price": float(p.min()),
        "max_price": float(p.max()),
        "avg_price": float(p.mean()),
    }


@st.cache_data(show_spinner=False)
def category_summary(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    if df.empty or "category" not in col_map or "price" not in col_map:
        return pd.DataFrame()

    cat_col = col_map["category"]
    price_col = col_map["price"]

    if cat_col not in df.columns or price_col not in df.columns:
        return pd.DataFrame()

    out = (
        df.dropna(subset=[cat_col])
        .groupby(cat_col)[price_col]
        .agg(avg_price="mean", min_price="min", max_price="max", count="size")
        .reset_index()
        .rename(columns={cat_col: "category"})
    )
    return out.sort_values("avg_price", ascending=False)


@st.cache_data(show_spinner=False)
def platform_summary(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    if df.empty or "platform" not in col_map or "price" not in col_map:
        return pd.DataFrame()

    plat_col = col_map["platform"]
    price_col = col_map["price"]

    if plat_col not in df.columns or price_col not in df.columns:
        return pd.DataFrame()

    out = (
        df.dropna(subset=[plat_col])
        .groupby(plat_col)[price_col]
        .agg(avg_price="mean", min_price="min", max_price="max", count="size")
        .reset_index()
        .rename(columns={plat_col: "platform"})
    )
    return out.sort_values("avg_price", ascending=False)


@st.cache_data(show_spinner=False)
def discount_distribution(df: pd.DataFrame, col_map: dict, bins: int = 10) -> pd.DataFrame:
    if df.empty or "discount" not in col_map:
        return pd.DataFrame()

    disc_col = col_map["discount"]
    if disc_col not in df.columns:
        return pd.DataFrame()

    d = pd.to_numeric(df[disc_col], errors="coerce").dropna()
    if d.empty:
        return pd.DataFrame()

    hist, edges = np.histogram(d, bins=bins)
    labels = [f"{int(edges[i])}-{int(edges[i+1])}%" for i in range(len(edges)-1)]

    return pd.DataFrame({"discount_range": labels, "count": hist})


@st.cache_data(show_spinner=False)
def products_by_category(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    if df.empty or "category" not in col_map or "product_name" not in col_map:
        return pd.DataFrame()

    cat_col = col_map["category"]
    prod_col = col_map["product_name"]

    if cat_col not in df.columns or prod_col not in df.columns:
        return pd.DataFrame()

    out = (
        df.dropna(subset=[cat_col])
        .groupby(cat_col)[prod_col]
        .nunique()
        .reset_index(name="unique_products")
        .rename(columns={cat_col: "category"})
    )
    return out.sort_values("unique_products", ascending=False)


@st.cache_data(show_spinner=False)
def price_comparison_for_product(df: pd.DataFrame, col_map: dict, product_name: str) -> pd.DataFrame:
    """For selected product name, return per-platform prices (one row per platform).

    If there are duplicates for the same platform, we take the minimum price.
    """
    if df.empty or "product_name" not in col_map:
        return pd.DataFrame()

    prod_col = col_map["product_name"]
    if prod_col not in df.columns:
        return pd.DataFrame()

    matched = df[df[prod_col].astype(str) == str(product_name)].copy()
    if matched.empty:
        return pd.DataFrame()

    # Normalize numeric fields
    if "price" in col_map and col_map["price"] in matched.columns:
        matched[col_map["price"]] = pd.to_numeric(matched[col_map["price"]], errors="coerce")

    # Decide grouping key
    if "platform" in col_map and col_map["platform"] in matched.columns:
        group_col = col_map["platform"]
    else:
        group_col = None

    if group_col is None:
        # No platform column; just return raw rows
        return matched

    # Dynamically build agg dictionary using only existing columns
    agg_dict = {}
    if "price" in col_map and col_map["price"] in matched.columns:
        agg_dict["price"] = (col_map["price"], "min")
    if "original_price" in col_map and col_map["original_price"] in matched.columns:
        agg_dict["original_price"] = (col_map["original_price"], "max")
    if "discount" in col_map and col_map["discount"] in matched.columns:
        agg_dict["discount"] = (col_map["discount"], "max")
    if "rating" in col_map and col_map["rating"] in matched.columns:
        agg_dict["rating"] = (col_map["rating"], "max")
    if "availability" in col_map and col_map["availability"] in matched.columns:
        agg_dict["availability"] = (col_map["availability"], "first")
    if "product_url" in col_map and col_map["product_url"] in matched.columns:
        agg_dict["product_url"] = (col_map["product_url"], "first")
    if "category" in col_map and col_map["category"] in matched.columns:
        agg_dict["category"] = (col_map["category"], "first")

    if not agg_dict:
        return pd.DataFrame()

    agg = (
        matched.dropna(subset=[group_col])
        .groupby(group_col)
        .agg(**agg_dict)
        .reset_index()
    )

    agg = agg.rename(columns={group_col: "platform"})

    if "price" in agg.columns:
        agg["price"] = pd.to_numeric(agg["price"], errors="coerce")
        return agg.sort_values("price", ascending=True)

    return agg


@st.cache_data(show_spinner=False)
def compute_price_insight(df: pd.DataFrame, col_map: dict, product_name: str) -> dict:
    """Compute lowest/highest/average and potential saving.

    For price history trend: only if scraped_date exists.
    """
    comp = price_comparison_for_product(df, col_map, product_name)
    if comp.empty or "price" not in comp.columns:
        return {}

    prices = comp["price"].dropna()
    if prices.empty:
        return {}

    lowest = float(prices.min())
    highest = float(prices.max())
    avg = float(prices.mean())

    # Potential saving vs average
    potential_saving = avg - lowest

    insight = {
        "lowest_price": lowest,
        "highest_price": highest,
        "average_price": avg,
        "potential_saving": float(potential_saving) if not np.isnan(potential_saving) else None,
    }

    # Optional price history
    if "scraped_date" in col_map and "price" in col_map and "product_name" in col_map:
        prod_col = col_map["product_name"]
        date_col = col_map["scraped_date"]
        price_col = col_map["price"]

        hist = df[df[prod_col].astype(str) == str(product_name)].copy()
        hist[date_col] = pd.to_datetime(hist[date_col], errors="coerce")
        hist[price_col] = pd.to_numeric(hist[price_col], errors="coerce")

        hist = hist.dropna(subset=[date_col, price_col])
        if not hist.empty:
            # Take minimum price per day (or per date value)
            hist = (
                hist.groupby(hist[date_col])
                .agg(current_price=(price_col, "min"))
                .reset_index()
                .rename(columns={date_col: "scraped_date"})
                .sort_values("scraped_date")
            )

            insight["history_available"] = True
            insight["history"] = hist

            if len(hist) >= 2:
                insight["previous_price"] = float(hist["current_price"].iloc[-2])
                insight["current_price"] = float(hist["current_price"].iloc[-1])
                insight["price_change"] = float(hist["current_price"].iloc[-1] - hist["current_price"].iloc[-2])
            else:
                insight["history_available"] = True

    return insight
