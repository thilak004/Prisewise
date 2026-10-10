"""Debug script to check image_data column in CSV and products_overview output."""

import os
import pandas as pd
from utils.data_loader import load_data
from utils.product_select import products_overview

# Check CSV directly
df = pd.read_csv("data/pricewise_data.csv")
print("=== CSV Check ===")
print(f"Columns: {list(df.columns)}")
print(f"image_data exists: {'image_data' in df.columns}")
if "image_data" in df.columns:
    print(f"First 3 values:")
    for v in df["image_data"].head(3):
        print(f"  {v}")
    print(f"Starts with assets/: {df['image_data'].str.startswith('assets/').sum()}")
    print(f"Starts with data:image: {df['image_data'].str.startswith('data:image').sum()}")

# Check products_overview
print("\n=== products_overview Check ===")
df2, col_map, _ = load_data()
overview = products_overview(df2, col_map)
print(f"Overview columns: {list(overview.columns)}")
print(f"image_data in overview: {'image_data' in overview.columns}")
if "image_data" in overview.columns:
    print(f"First 3 values:")
    for v in overview["image_data"].head(3):
        print(f"  {v}")

# Check if files exist
print("\n=== File Existence Check ===")
if "image_data" in overview.columns:
    for v in overview["image_data"].head(5):
        if isinstance(v, str) and v.startswith("assets/"):
            exists = os.path.exists(v)
            print(f"  {v} -> exists: {exists}")
