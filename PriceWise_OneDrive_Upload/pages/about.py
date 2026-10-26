import streamlit as st


def main():
    st.title("About PriceWise")

    if st.button("← Back to Home", type="secondary"):
        st.switch_page("pages/home.py")

    st.divider()

    st.subheader("What is PriceWise?")
    st.write(
        "PriceWise is a simple product price analysis and comparison web app. "
        "It reads product offers from a CSV file, compares prices across platforms (stores), "
        "and shows useful analytics like best price, price range, discounts, and trends."
    )

    st.subheader("Problem Statement")
    st.write(
        "When shopping online, it’s hard to quickly compare prices from multiple stores. "
        "PriceWise makes this easier by automatically organizing data and highlighting the best available deal."
    )

    st.subheader("Objectives")
    st.markdown(
        "- Compare current prices across different platforms\n"
        "- Identify the lowest, highest, and average price\n"
        "- Show discounts and category-wise analytics\n"
        "- Provide simple price insights (and trends if history exists in the CSV)"
    )

    st.subheader("Technologies Used")
    st.markdown(
        "- Python\n"
        "- Streamlit (UI)\n"
        "- Pandas (data cleaning & analysis)\n"
        "- Plotly (charts)\n"
        "- CSV (initial data source)"
    )

    st.subheader("Basic Workflow")
    st.markdown(
        "1. Load product offers from `data/pricewise_data.csv`\n"
        "2. Detect which columns exist (so missing optional columns won't crash the app)\n"
        "3. Let users search, filter by category/platform, and select a product\n"
        "4. Show price comparison + charts and analytics"
    )

    st.divider()

    st.subheader("Future Improvements")
    st.markdown(
        "PriceWise can be extended later with:"
        "\n- Live web scraping\n"
        "- SQLite/MySQL database\n"
        "- Price history + alerts\n"
        "- Machine learning prediction\n"
        "- User login, wishlist, and more"
    )


if __name__ == "__main__":
    main()
