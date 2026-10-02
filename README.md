# PriceWise (Student Project)

## 1) Project Overview
PriceWise is a product price analysis and comparison system. It reads product offers from a CSV file and helps users:
- compare prices across multiple platforms/stores
- find the lowest available deal
- view simple price analytics and trends (if history exists in the CSV)

> Data collection & cleaning are expected to be done separately in Google Colab.

## 2) Features (First Version)
- **Home page**
  - Search products
  - Filter by category, platform, and price range
  - Select a product and jump to comparison
- **Product Search & Results**
  - Displays product name, best available platform, price, original price, discount, rating (if available), and product URL (if available)
- **Price Comparison**
  - Lowest / highest / average price
  - Potential saving vs average
  - Plotly bar chart for price comparison
  - Optional price history trend (only if `scraped_date` exists in CSV)
- **Analytics**
  - Average price by category
  - Average price by platform
  - Discount distribution
  - Number of products by category
- **About page**
  - Simple explanation suitable for a college demonstration

## 3) Technology Stack
- Python
- Streamlit
- Pandas
- Plotly
- CSV (initially)

## 4) Project Structure
```text
PriceWise/
│
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── pricewise_data.csv
│
├── pages/
│   ├── home.py
│   ├── comparison.py
│   ├── analytics.py
│   └── about.py
│
├── utils/
│   ├── data_loader.py
│   └── analysis.py
│
└── assets/
    └── logo.png
```

## 5) How to Install Dependencies
From the project folder:

```bash
pip install -r requirements.txt
```

## 6) How to Run the Application
```bash
streamlit run app.py
```

## 7) Replacing the Sample CSV with Colab Output
1. Open Google Colab and export your output to a CSV.
2. Copy/rename it to:

- `data/pricewise_data.csv`

3. Run the app again.

### Expected CSV Format (Column Detection)
The app is flexible and will detect which columns exist.

Recommended (but not all required):
- `product_name`
- `category`
- `platform`
- `price`
- `original_price`
- `discount` (percentage)
- `rating`
- `availability`
- `product_url`
- `scraped_date`

If some optional columns are missing, the UI hides the corresponding elements and the app still works.

## 8) Deploy the App
For deployment you can use common Streamlit platforms (e.g., Streamlit Community Cloud). Make sure:
- `app.py`, `pages/`, `utils/`, and `requirements.txt` are included
- `data/pricewise_data.csv` is present (or loaded from a compatible path)

```
"# Prisewise" 
