import os
import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.product_select import products_overview, search_overview, fuzzy_search_products
from utils.sidebar import sidebar_filters
from utils.formatting import format_inr, format_percent
from utils.analysis import best_deal_score, add_to_watchlist, remove_from_watchlist, is_in_watchlist, get_watchlist


def main():
    # Load data
    df, col_map, is_sample = load_data()

    # Header area
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("assets/logo.png") and os.path.getsize("assets/logo.png") > 100:
            st.image("assets/logo.png", width=80)
        else:
            st.markdown("## 📊")
    with col2:
        st.title("PriceWise")
        st.caption("Compare product prices, analyze price trends, and find the best available deal.")

    # ── Feature #8: Auto-complete Search ──────────────────────────────────
    st.subheader("Search Products")

    # Get all product names for auto-complete
    all_products = []
    if not df.empty and "product_name" in col_map:
        prod_col = col_map["product_name"]
        if prod_col in df.columns:
            all_products = sorted(df[prod_col].dropna().astype(str).unique().tolist())

    # Auto-complete suggestions
    search_query = st.text_input("Enter product name", placeholder="e.g., iPhone 16, Samsung Galaxy S24...")

    # Show auto-complete suggestions
    if search_query and len(search_query) >= 2:
        suggestions = fuzzy_search_products(df, col_map, search_query, max_results=5)
        if suggestions:
            with st.expander("Suggestions", expanded=True):
                for sugg in suggestions:
                    if st.button(sugg, key=f"sugg_{sugg}", use_container_width=True):
                        st.session_state.search_query = sugg
                        st.rerun()

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_button = st.button("Search", type="primary")
    with col2:
        show_all = st.button("Show All Products")
    with col3:
        # ── Feature #15: Watchlist button ─────────────────────────────────
        watchlist = get_watchlist()
        if watchlist:
            if st.button(f"Watchlist ({len(watchlist)})", type="secondary"):
                st.session_state.show_watchlist = not st.session_state.get("show_watchlist", False)
                st.rerun()
        else:
            st.button("Watchlist (0)", disabled=True)

    # Apply filters and get products overview for selection
    filtered_df = df.copy()
    if not df.empty:
        filtered_df = sidebar_filters(df, col_map, show_navigation=False)

    # Get overview products (one per product_name, best price)
    overview_df = products_overview(filtered_df, col_map)

    # ── Feature #2: Best Deal Score ──────────────────────────────────────
    deal_df = best_deal_score(filtered_df, col_map)
    deal_map = {}
    if not deal_df.empty:
        for _, row in deal_df.iterrows():
            key = (row.get("product_name", ""), row.get("platform", ""))
            deal_map[key] = {"score": row.get("score", 0), "tier": row.get("deal_tier", "")}

    # Determine what to show
    show_watchlist = st.session_state.get("show_watchlist", False)

    if show_watchlist:
        # Show watchlist products
        watchlist = get_watchlist()
        if watchlist:
            display_df = overview_df[overview_df["product_name"].isin(watchlist)].copy() if not overview_df.empty else pd.DataFrame()
            show_title = "My Watchlist"
        else:
            display_df = pd.DataFrame()
            show_title = "My Watchlist (Empty)"
    elif show_all or (not search_query and not search_button):
        display_df = overview_df
        show_title = "All Products"
    elif search_query:
        display_df = search_overview(overview_df, search_query)
        show_title = f"Search Results for '{search_query}'"
        if display_df.empty:
            st.warning(f"No products found matching '{search_query}'. Try a different search term.")
    else:
        display_df = overview_df
        show_title = "All Products"

    # Show results
    st.subheader(show_title)

    if display_df.empty:
        st.info("No products to display.")
        return

    # Display results in a nice format
    for idx, row in display_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])

            with col1:
                product_name = row.get("product_name", "Unknown Product")
                st.write(f"**{product_name}**")

                # Show category and platform if available
                details = []
                if "category" in row and pd.notna(row["category"]):
                    details.append(str(row["category"]))
                if "platform" in row and pd.notna(row["platform"]):
                    details.append(str(row["platform"]))
                if details:
                    st.caption(" • ".join(details))

            with col2:
                if "price" in row and pd.notna(row["price"]):
                    st.metric("Price", format_inr(row["price"]))
                else:
                    st.metric("Price", "N/A")

            with col3:
                if "discount" in row and pd.notna(row["discount"]):
                    st.metric("Discount", format_percent(row["discount"]))
                else:
                    st.metric("Discount", "N/A")

            with col4:
                # ── Feature #2: Best Deal Badge ────────────────────────────
                deal_info = deal_map.get((row.get("product_name", ""), row.get("platform", "")), None)
                if deal_info:
                    tier = deal_info["tier"]
                    tier_color = {"Excellent": "green", "Good": "blue", "Average": "orange", "Poor": "red"}
                    st.markdown(f"**Deal:** :{tier_color.get(tier, 'gray')}[{tier}]")
                else:
                    st.write("")

            with col5:
                # ── Feature #15: Watchlist toggle ──────────────────────────
                product_name = row.get("product_name", "")
                if is_in_watchlist(product_name):
                    if st.button("Saved", key=f"wl_{idx}", use_container_width=True):
                        remove_from_watchlist(product_name)
                        st.rerun()
                else:
                    if st.button("+ Watch", key=f"wl_{idx}", use_container_width=True):
                        add_to_watchlist(product_name)
                        st.rerun()

            # View Details button
            if st.button("View Details", key=f"view_{idx}", use_container_width=True):
                st.session_state.selected_product = row.get("product_name")
                st.session_state.selected_category = row.get("category") if "category" in row and pd.notna(row["category"]) else None
                st.session_state.selected_platform = row.get("platform") if "platform" in row and pd.notna(row["platform"]) else None
                st.switch_page("pages/comparison.py")

            st.divider()

    # Show note about sample data if applicable
    if is_sample:
        st.info("Using sample data for demonstration. Replace data/pricewise_data.csv with your actual Google Colab data.")


if __name__ == "__main__":
    main()
