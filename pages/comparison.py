import os
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.analysis import (
    price_comparison_for_product,
    compute_price_insight,
    best_deal_score,
    add_to_watchlist,
    remove_from_watchlist,
    is_in_watchlist,
)
from utils.formatting import format_inr, format_percent, safe_str, is_valid_http_url


# ── cached helpers ──────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _multi_platform_products(df, col_map):
    """Products that appear on 2+ platforms with the exact same name."""
    prod_col = col_map.get("product_name")
    plat_col = col_map.get("platform")
    if not prod_col or not plat_col:
        return []
    counts = df.groupby(prod_col)[plat_col].nunique()
    return sorted(counts[counts > 1].index.tolist())


@st.cache_data(show_spinner=False)
def _all_products(df, col_map):
    prod_col = col_map.get("product_name")
    if not prod_col or prod_col not in df.columns:
        return []
    return sorted(df[prod_col].dropna().astype(str).unique().tolist())


@st.cache_data(show_spinner=False)
def _category_platform_best(df, col_map, category):
    """Cheapest product per platform within a given category."""
    cat_col   = col_map.get("category")
    plat_col  = col_map.get("platform")
    prod_col  = col_map.get("product_name")
    price_col = col_map.get("price")

    if not all([cat_col, plat_col, prod_col, price_col]):
        return pd.DataFrame()

    cat_df = df[df[cat_col].astype(str) == category].copy()
    if cat_df.empty:
        return pd.DataFrame()

    cat_df[price_col] = pd.to_numeric(cat_df[price_col], errors="coerce")
    cat_df = cat_df.dropna(subset=[price_col])

    idx  = cat_df.groupby(plat_col)[price_col].idxmin()
    best = cat_df.loc[idx].copy().sort_values(price_col, ascending=True)

    out_cols = {prod_col: "product_name", plat_col: "platform", price_col: "price"}
    for canonical, col_name in [("discount", "discount"), ("rating", "rating"), ("availability", "availability")]:
        c = col_map.get(canonical)
        if c and c in best.columns:
            out_cols[c] = col_name

    best = best.rename(columns=out_cols)
    keep = [v for v in out_cols.values() if v in best.columns]
    return best[keep].reset_index(drop=True)


# ── page ────────────────────────────────────────────────────────────────────

def main():
    df, col_map, is_sample = load_data()

    if df.empty:
        st.warning("No data found. Please check your CSV file.")
        if st.button("Go to Home"):
            st.switch_page("pages/home.py")
        return

    all_prods   = _all_products(df, col_map)
    multi_prods = _multi_platform_products(df, col_map)

    # Header
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("assets/logo.png") and os.path.getsize("assets/logo.png") > 100:
            st.image("assets/logo.png", width=60)
        else:
            st.markdown("## 📊")
    with col2:
        st.title("Price Comparison")
        if st.button("← Back to Products"):
            st.switch_page("pages/home.py")

    # ── Feature #14: Live Scraping Demo Button ─────────────────────────────
    with st.expander("Live Scraping Demo"):
        st.write("Click the button below to simulate scraping a product from a live source.")
        st.warning("Note: This is a demo. In production, this would connect to permitted e-commerce APIs.")
        if st.button("Scrape Live Data", type="primary"):
            with st.spinner("Scraping product data..."):
                import time
                time.sleep(2)  # Simulate network delay
                st.success("Scraped 15 new offers from 3 platforms!")
                st.info("In a live deployment, this would fetch real-time prices from Amazon, Flipkart, etc.")

    tab1, tab2 = st.tabs(["Exact Product Comparison", "Compare by Category"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — exact name match across platforms
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        if multi_prods:
            st.success(f"**{len(multi_prods)}** products found on multiple platforms — fully comparable.")
            prod_options = multi_prods
        else:
            st.warning(
                "No products in your dataset share the **exact same name** across multiple platforms. "
                "This means direct comparison isn't possible here. "
                "Use the **Compare by Category** tab to compare the best deals on each platform."
            )
            prod_options = all_prods

        if not prod_options:
            st.info("No products available.")
        else:
            default_prod = st.session_state.get("selected_product")
            default_idx  = 0
            if default_prod and default_prod in prod_options:
                default_idx = prod_options.index(default_prod)

            selected_prod = st.selectbox(
                "Select Product",
                options=prod_options,
                index=default_idx,
                help="Products listed on 2+ platforms are shown first.",
            )
            st.session_state.selected_product = selected_prod

            st.divider()

            comparison_df = price_comparison_for_product(df, col_map, selected_prod)
            insight       = compute_price_insight(df, col_map, selected_prod)

            if comparison_df.empty:
                st.error(f"No price data found for '{selected_prod}'.")
            else:
                num_platforms = len(comparison_df)
                st.subheader(f"📦 {selected_prod}")

                # ── Feature #15: Watchlist toggle ─────────────────────────
                if is_in_watchlist(selected_prod):
                    if st.button("Remove from Watchlist", key="wl_remove"):
                        remove_from_watchlist(selected_prod)
                        st.rerun()
                else:
                    if st.button("Add to Watchlist", key="wl_add"):
                        add_to_watchlist(selected_prod)
                        st.rerun()

                # Quick facts from lowest-priced row
                prod_col = col_map.get("product_name")
                if prod_col and prod_col in df.columns:
                    product_rows = df[df[prod_col].astype(str) == str(selected_prod)].copy()
                    if not product_rows.empty:
                        price_col = col_map.get("price")
                        if price_col and price_col in product_rows.columns:
                            product_rows = product_rows.sort_values(price_col, ascending=True, na_position="last")
                        product_row = product_rows.iloc[0]
                        mc1, mc2, mc3, mc4 = st.columns(4)
                        with mc1:
                            cat_col = col_map.get("category")
                            if cat_col and cat_col in product_row and pd.notna(product_row[cat_col]):
                                st.metric("Category", safe_str(product_row[cat_col]))
                        with mc2:
                            if price_col and price_col in product_row and pd.notna(product_row[price_col]):
                                st.metric("Best Price", format_inr(product_row[price_col]))
                        with mc3:
                            disc_col = col_map.get("discount")
                            if disc_col and disc_col in product_row and pd.notna(product_row[disc_col]):
                                st.metric("Discount", format_percent(product_row[disc_col]))
                        with mc4:
                            rat_col = col_map.get("rating")
                            if rat_col and rat_col in product_row and pd.notna(product_row[rat_col]):
                                st.metric("Rating", f"{product_row[rat_col]:.1f} /5")

                # ── Feature #2: Best Deal Recommendation ──────────────────
                deal_df = best_deal_score(df, col_map)
                if not deal_df.empty:
                    # Find best deal for this product
                    prod_deals = deal_df[deal_df["product_name"] == selected_prod]
                    if not prod_deals.empty:
                        best = prod_deals.iloc[0]
                        st.success(
                            f"**Best Deal:** {best.get('platform', 'N/A')} — "
                            f"{format_inr(best.get('price', 0))} "
                            f"(Score: {best.get('score', 0):.2f}, {best.get('deal_tier', 'N/A')})"
                        )

                # Single-platform notice
                if num_platforms == 1:
                    plat_val = comparison_df["platform"].iloc[0] if "platform" in comparison_df.columns else "1 site"
                    st.info(
                        f"**'{selected_prod}'** is only listed on **{plat_val}** in your dataset. "
                        "Switch to the **Compare by Category** tab to find similar products across platforms."
                    )

                st.divider()
                st.subheader("Price Across Platforms")

                # ── Feature #11: Sortable Data Table ───────────────────────
                dcols = [c for c in ["platform", "price", "discount", "rating", "availability"] if c in comparison_df.columns]
                display_df = comparison_df[dcols].copy()
                if "price"        in display_df.columns:
                    display_df["price"]        = display_df["price"].apply(format_inr)
                if "discount"     in display_df.columns:
                    display_df["discount"]     = display_df["discount"].apply(format_percent)
                if "rating"       in display_df.columns:
                    display_df["rating"]       = display_df["rating"].apply(
                        lambda x: f"{x:.1f} /5" if pd.notna(x) else "N/A")
                if "availability" in display_df.columns:
                    display_df["availability"] = display_df["availability"].fillna("N/A")

                display_df = display_df.rename(columns={
                    "platform": "Platform", "price": "Price",
                    "discount": "Discount", "rating": "Rating", "availability": "Availability",
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # ── Feature #11: Export to CSV ─────────────────────────────
                csv = comparison_df.to_csv(index=False)
                st.download_button(
                    label="Download Comparison as CSV",
                    data=csv,
                    file_name=f"pricewise_comparison_{selected_prod[:30].replace(' ', '_')}.csv",
                    mime="text/csv",
                )

                # Insights
                if insight and num_platforms > 1:
                    st.subheader("Price Insights")
                    ic1, ic2, ic3, ic4 = st.columns(4)
                    ic1.metric("Lowest",      format_inr(insight.get("lowest_price")))
                    ic2.metric("Highest",     format_inr(insight.get("highest_price")))
                    ic3.metric("Average",     format_inr(insight.get("average_price")))
                    saving = insight.get("potential_saving")
                    ic4.metric("You Can Save", format_inr(saving) if saving else "N/A")

                # Price History Chart (if available)
                if insight and insight.get("history_available") and "history" in insight:
                    st.divider()
                    st.subheader("Price History")
                    hist_df = insight["history"]
                    if not hist_df.empty and len(hist_df) >= 2:
                        fig = px.line(
                            hist_df, x="scraped_date", y="current_price",
                            title=f"Price Trend: {selected_prod}",
                            labels={"scraped_date": "Date", "current_price": "Price (₹)"},
                            markers=True,
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Price change indicator
                        if "price_change" in insight:
                            change = insight["price_change"]
                            if change < 0:
                                st.success(f"Price dropped by {format_inr(abs(change))} since last scrape!")
                            elif change > 0:
                                st.warning(f"Price increased by {format_inr(change)} since last scrape.")
                            else:
                                st.info("Price unchanged since last scrape.")

                # Bar chart
                if "platform" in comparison_df.columns and "price" in comparison_df.columns and num_platforms > 1:
                    chart_df = comparison_df.dropna(subset=["platform", "price"]).copy()
                    chart_df["price"] = pd.to_numeric(chart_df["price"], errors="coerce")
                    chart_df = chart_df.dropna(subset=["price"])
                    if not chart_df.empty:
                        fig = px.bar(
                            chart_df, x="platform", y="price",
                            title=f"Price Comparison: {selected_prod}",
                            labels={"platform": "Platform", "price": "Price (₹)"},
                            color="price", color_continuous_scale="RdYlGn_r",
                        )
                        fig.update_layout(showlegend=False, coloraxis_showscale=False)
                        st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — category-level cross-platform comparison
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### Best Deals Across Platforms by Category")
        st.caption(
            "Shows the **cheapest product** available on each platform within the chosen category. "
            "Perfect when the same product isn't listed everywhere with the same name."
        )

        cat_col = col_map.get("category")
        if not cat_col or cat_col not in df.columns:
            st.warning("Category data not available in your dataset.")
        else:
            categories = sorted(df[cat_col].dropna().astype(str).unique().tolist())
            sel_cat_sess = st.session_state.get("selected_category")
            cat_default  = 0
            if sel_cat_sess and sel_cat_sess in categories:
                cat_default = categories.index(sel_cat_sess)

            selected_cat = st.selectbox("Select Category", options=categories, index=cat_default)
            st.divider()

            best_df = _category_platform_best(df, col_map, selected_cat)

            if best_df.empty:
                st.info(f"No data available for category: {selected_cat}")
            else:
                num_p = len(best_df)
                st.success(f"Found **{num_p} platforms** selling **{selected_cat}** products.")

                # Metric cards — one per platform
                st.subheader(f"Best Deal per Platform — {selected_cat}")
                cols = st.columns(min(num_p, 5))
                for i, (_, row) in enumerate(best_df.iterrows()):
                    with cols[i % len(cols)]:
                        plat  = row.get("platform", "N/A")
                        price = row.get("price")
                        prod  = row.get("product_name", "N/A")
                        disc  = row.get("discount")
                        rat   = row.get("rating")
                        st.markdown(f"**{plat}**")
                        if pd.notna(price):
                            st.metric("Best Price", format_inr(price))
                        if pd.notna(disc):
                            st.caption(f"{format_percent(disc)} off")
                        if pd.notna(rat):
                            st.caption(f"{rat:.1f}/5")
                        st.caption(f"_{prod}_")

                st.divider()

                # Full table
                st.subheader("Full Comparison Table")
                disp = best_df.copy()
                if "price"    in disp.columns:
                    disp["price"]    = disp["price"].apply(format_inr)
                if "discount" in disp.columns:
                    disp["discount"] = disp["discount"].apply(format_percent)
                if "rating"   in disp.columns:
                    disp["rating"]   = disp["rating"].apply(
                        lambda x: f"{x:.1f} /5" if pd.notna(x) else "N/A")

                disp = disp.rename(columns={
                    "platform": "Platform", "product_name": "Best Product",
                    "price": "Price", "discount": "Discount",
                    "rating": "Rating", "availability": "Availability",
                })
                st.dataframe(disp, use_container_width=True, hide_index=True)

                # Bar chart
                chart_src = best_df.dropna(subset=["platform", "price"]).copy()
                chart_src["price"] = pd.to_numeric(chart_src["price"], errors="coerce")
                if not chart_src.empty:
                    hover = ["product_name"] if "product_name" in chart_src.columns else None
                    fig = px.bar(
                        chart_src, x="platform", y="price", color="platform",
                        title=f"Best {selected_cat} Price per Platform",
                        labels={"platform": "Platform", "price": "Best Price (₹)"},
                        hover_data=hover,
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

    if is_sample:
        st.info("Using sample data for demonstration.")


if __name__ == "__main__":
    main()
