import os
import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.analysis import (
    basic_stats,
    category_summary,
    platform_summary,
    discount_distribution,
    products_by_category,
    category_discount_summary,
    platform_market_share,
    train_price_predictor,
    predict_deal_quality,
)
from utils.sidebar import sidebar_filters
from utils.formatting import format_inr


def main():
    df, col_map, is_sample = load_data()

    # Header
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("assets/logo.png") and os.path.getsize("assets/logo.png") > 100:
            st.image("assets/logo.png", width=50)
        else:
            st.markdown("## ")
    with col2:
        st.title("Analytics")
        if st.button("← Back to Home", type="secondary"):
            st.switch_page("pages/home.py")

    # Sidebar filters (with navigation)
    st.sidebar.title("PriceWise")
    filtered_df = sidebar_filters(df, col_map, show_navigation=True)

    if df.empty:
        st.warning("No data found. Please check your CSV file.")
        return

    if filtered_df.empty:
        st.warning("No products match your filters.")
        return

    # Basic stats
    stats = basic_stats(filtered_df, col_map)
    st.subheader("Summary")
    s1, s2, s3 = st.columns(3)

    s1.metric("Minimum Price", format_inr(stats.get("min_price")))
    s2.metric("Maximum Price", format_inr(stats.get("max_price")))
    s3.metric("Average Price", format_inr(stats.get("avg_price")))

    st.divider()

    # Average price by category
    st.subheader("Average Price by Category")
    cat_df = category_summary(filtered_df, col_map)
    if not cat_df.empty:
        fig = px.bar(
            cat_df,
            x="category",
            y="avg_price",
            title="Average price (₹) per category",
            labels={"category": "Category", "avg_price": "Average Price (₹)"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Category data or price data is missing in your CSV.")

    st.divider()

    # ── Feature #7: Category-wise Average Discount ─────────────────────────
    st.subheader("Average Discount by Category")
    disc_cat_df = category_discount_summary(filtered_df, col_map)
    if not disc_cat_df.empty:
        fig = px.bar(
            disc_cat_df,
            x="category",
            y="avg_discount",
            title="Which category has the deepest discounts?",
            labels={"category": "Category", "avg_discount": "Average Discount (%)"},
            color="avg_discount",
            color_continuous_scale="Greens",
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        # Show table too
        st.dataframe(disc_cat_df, use_container_width=True, hide_index=True)
    else:
        st.info("Discount or category data is missing in your CSV.")

    st.divider()

    # Price comparison by platform
    st.subheader("Price Comparison by Platform")
    plat_df = platform_summary(filtered_df, col_map)
    if not plat_df.empty:
        fig = px.bar(
            plat_df,
            x="platform",
            y="avg_price",
            title="Average price (₹) per platform",
            labels={"platform": "Platform", "avg_price": "Average Price (₹)"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Platform data or price data is missing in your CSV.")

    st.divider()

    # ── Feature #11: Platform Market Share Pie Chart ───────────────────────
    st.subheader("Platform Market Share")
    share_df = platform_market_share(filtered_df, col_map)
    if not share_df.empty:
        fig = px.pie(
            share_df,
            values="product_count",
            names="platform",
            title="Number of products per platform",
            hover_data=["market_share_pct"] if "market_share_pct" in share_df.columns else None,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Platform data is missing in your CSV.")

    st.divider()

    # Discount distribution
    st.subheader("Discount Distribution")
    disc_df = discount_distribution(filtered_df, col_map, bins=10)
    if not disc_df.empty:
        fig = px.bar(
            disc_df,
            x="discount_range",
            y="count",
            title="How discounts are distributed",
            labels={"discount_range": "Discount Range", "count": "Number of offers"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Discount data is missing in your CSV.")

    st.divider()

    # Number of products by category
    st.subheader("Number of Products by Category")
    count_cat_df = products_by_category(filtered_df, col_map)
    if not count_cat_df.empty:
        fig = px.bar(
            count_cat_df,
            x="category",
            y="unique_products",
            title="Product count per category",
            labels={"category": "Category", "unique_products": "Number of Products"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Category data is missing in your CSV.")

    st.divider()

    # ── Feature #13: ML Price Prediction ───────────────────────────────────
    st.subheader("ML Price Prediction")
    st.caption("Uses scikit-learn Logistic Regression to predict if a product is a 'good deal'.")

    model, encoder, feature_columns, accuracy = train_price_predictor(filtered_df, col_map)

    if model is not None:
        st.success(f"Model trained successfully! Accuracy: {accuracy:.1%}")

        # Input form for prediction
        st.write("Enter product details to predict if it's a good deal:")
        pc1, pc2, pc3, pc4 = st.columns(4)

        cat_col = col_map.get("category")
        plat_col = col_map.get("platform")
        disc_col = col_map.get("discount")
        rat_col = col_map.get("rating")

        with pc1:
            if cat_col and cat_col in filtered_df.columns:
                categories = sorted(filtered_df[cat_col].dropna().astype(str).unique().tolist())
                pred_category = st.selectbox("Category", options=categories, key="pred_cat")
            else:
                pred_category = st.text_input("Category", key="pred_cat")

        with pc2:
            if plat_col and plat_col in filtered_df.columns:
                platforms = sorted(filtered_df[plat_col].dropna().astype(str).unique().tolist())
                pred_platform = st.selectbox("Platform", options=platforms, key="pred_plat")
            else:
                pred_platform = st.text_input("Platform", key="pred_plat")

        with pc3:
            pred_discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=10.0, key="pred_disc")

        with pc4:
            pred_rating = st.number_input("Rating (0-5)", min_value=0.0, max_value=5.0, value=4.0, key="pred_rat")

        if st.button("Predict Deal Quality", type="primary"):
            input_data = {
                "category": pred_category,
                "platform": pred_platform,
                "discount": pred_discount,
                "rating": pred_rating,
            }
            result = predict_deal_quality(model, encoder, feature_columns, input_data)

            if result.get("prediction") is not None:
                if result["is_good_deal"]:
                    st.success(f"**Good Deal!** (Confidence: {result['probability']:.1%})")
                else:
                    st.error(f"**Not a Good Deal** (Confidence: {result['probability']:.1%})")
            else:
                st.warning("Could not make prediction. Check your inputs.")
    else:
        st.info("Not enough data to train ML model. Need at least 20 products with price data.")

    if is_sample:
        st.info("Using sample data. Replace data/pricewise_data.csv with your Colab-generated CSV for real results.")


if __name__ == "__main__":
    main()
